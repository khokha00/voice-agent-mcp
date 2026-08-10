"""Phase 1 end-to-end acceptance test: 5 varied questions through the full
Planner -> Researcher -> Writer graph, per CHARTER.md Phase 1 definition of done."""
from src.state import GraphState
from src.graph import build_phase1_graph

TEST_QUESTIONS = [
    "What caused the 2008 financial crisis?",
    "How does CRISPR gene editing work?",
    "What are the environmental impacts of lithium mining?",
    "What is the current state of fusion energy research?",
    "How do mRNA vaccines work?",
]

if __name__ == "__main__":
    graph = build_phase1_graph()

    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*60}\n[{i}/5] {q}\n{'='*60}")
        try:
            result = graph.invoke(GraphState(question=q))
            print(f"Plan steps: {len(result['plan'])}")
            print(f"Findings: {len(result['findings'])}")
            print(f"\n--- Report ---\n{result['draft_report']}\n")
        except Exception as e:
            print(f"FAILED: {e}")