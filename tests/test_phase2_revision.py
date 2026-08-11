"""Phase 2 acceptance test: verify the revision loop actually fires and terminates.
Builds a standalone mini-graph entering at `critic` so the deliberately weak,
pre-injected state is what actually gets judged (the full pipeline's entry point
is `planner`, which would overwrite our injected findings/draft before Critic
ever sees them).

Route rule: after ANY revision (researcher or writer), we always pass through
`writer` before going back to `critic` — new research is only useful if the
report actually gets rewritten to use it. `researcher` never routes straight
to `critic`."""
from langgraph.graph import StateGraph, END
from src.state import GraphState, Finding, ResearchStep
from src.agents.critic import critic_node
from src.agents.writer import writer_node
from src.agents.researcher import researcher_node


def _route_after_critic(state: GraphState) -> str:
    verdict = state.critic_verdict
    if verdict is None or verdict.route_to == "done":
        return "done"
    if state.revision_count >= state.max_revisions:
        return "done"
    return verdict.route_to


def _bump_to_researcher(state: GraphState) -> dict:
    return {"revision_count": state.revision_count + 1}


def _bump_to_writer(state: GraphState) -> dict:
    return {"revision_count": state.revision_count + 1}


def build_critic_loop_test_graph():
    graph = StateGraph(GraphState)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("bump_to_researcher", _bump_to_researcher)
    graph.add_node("bump_to_writer", _bump_to_writer)

    graph.set_entry_point("critic")
    graph.add_conditional_edges(
        "critic", _route_after_critic,
        {"researcher": "bump_to_researcher", "writer": "bump_to_writer", "done": END},
    )
    graph.add_edge("bump_to_researcher", "researcher")
    graph.add_edge("researcher", "writer")   # always rewrite after new research
    graph.add_edge("bump_to_writer", "writer")
    graph.add_edge("writer", "critic")       # single path back to critic

    return graph.compile()


if __name__ == "__main__":
    graph = build_critic_loop_test_graph()

    weak_state = GraphState(
        question="What are the environmental impacts of lithium mining?",
        plan=[ResearchStep(question="What are the environmental impacts of lithium mining?")],
        findings=[
            Finding(claim="Lithium mining uses water.", source_url="https://example.com")
        ],
        draft_report="Lithium mining is bad for the environment in many ways, "
                      "including causing cancer in nearby towns and destroying "
                      "entire ecosystems within months.",
    )

    result = graph.invoke(weak_state)

    print(f"Final revision_count: {result['revision_count']} (cap: {weak_state.max_revisions})")
    print(f"Final verdict: {result['critic_verdict']}")
    print(f"\n--- Final report ---\n{result['draft_report']}")

    changed = result["draft_report"] != weak_state.draft_report
    print(f"\nReport actually rewritten: {changed}")

    assert result["revision_count"] > 0, "FAIL: Critic approved a weak draft without any revision"
    assert result["revision_count"] <= weak_state.max_revisions, "FAIL: revision cap not respected"
    assert changed, "FAIL: loop ran but never produced a new report from the revised findings"
    print("\n✅ Revision loop fired, rewrote the report, and respected the cap.")