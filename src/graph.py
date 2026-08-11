"""LangGraph wiring: Planner -> Researcher -> Writer -> Critic, with revision loop."""
from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.agents.planner import planner_node
from src.agents.researcher import researcher_node
from src.agents.writer import writer_node
from src.agents.critic import critic_node


def _route_after_critic(state: GraphState) -> str:
    """Decide where to go after the Critic, enforcing the hard revision cap."""
    verdict = state.critic_verdict

    if verdict is None or verdict.route_to == "done":
        return "done"

    if state.revision_count >= state.max_revisions:
        return "done"  # cap hit — stop looping even if Critic wants another pass

    return verdict.route_to  # "researcher" or "writer"


def _bump_then_researcher(state: GraphState) -> dict:
    return {"revision_count": state.revision_count + 1}


def _bump_then_writer(state: GraphState) -> dict:
    return {"revision_count": state.revision_count + 1}


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("bump_to_researcher", _bump_then_researcher)
    graph.add_node("bump_to_writer", _bump_then_writer)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")

    graph.add_conditional_edges(
        "critic",
        _route_after_critic,
        {
            "researcher": "bump_to_researcher",
            "writer": "bump_to_writer",
            "done": END,
        },
    )
    graph.add_edge("bump_to_researcher", "researcher")
    graph.add_edge("bump_to_writer", "writer")

    return graph.compile()