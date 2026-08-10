"""Manual smoke test: Planner -> Researcher chained together."""
from src.state import GraphState
from src.agents.planner import planner_node
from src.agents.researcher import researcher_node

if __name__ == "__main__":
    question = "What are the environmental impacts of lithium mining?"
    state = GraphState(question=question)

    plan_update = planner_node(state)
    state = state.model_copy(update=plan_update)
    print("Plan:")
    for step in state.plan:
        print(f"  - {step.question}")

    findings_update = researcher_node(state)
    print(f"\nFindings ({len(findings_update['findings'])}):")
    for f in findings_update["findings"]:
        print(f"  - {f.claim}\n    [{f.source_title}]({f.source_url})")