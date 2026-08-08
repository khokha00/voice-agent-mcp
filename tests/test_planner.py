"""Manual smoke test for the Planner node. Run directly, not via pytest yet
(no mocking infra set up until we decide on a testing strategy in a later ticket)."""
from src.state import GraphState
from src.agents.planner import planner_node

TEST_QUESTIONS = [
    "What caused the 2008 financial crisis?",
    "How does CRISPR gene editing work?",
    "What are the environmental impacts of lithium mining?",
]

if __name__ == "__main__":
    for q in TEST_QUESTIONS:
        state = GraphState(question=q)
        update = planner_node(state)
        print(f"\nQ: {q}")
        for step in update["plan"]:
            print(f"  - {step.question}")