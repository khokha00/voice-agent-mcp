"""Phase 3 acceptance test: verify the Researcher's tool router picks
different tools for different question types, and 'none' doesn't crash."""
from src.agents.researcher import _route_step

TEST_CASES = [
    ("What are the environmental impacts of lithium mining?", "web_search"),
    ("What did I write in my notes about the Q3 project plan?", "notion_search"),
    ("asdkjfh qpwoeiruqpwoeiru random gibberish query", "none"),  # sanity check for "none"
]

if __name__ == "__main__":
    for question, expected in TEST_CASES:
        actual = _route_step(question)
        status = "✅" if actual == expected else "⚠️ "
        print(f"{status} {question!r}\n    expected={expected}, got={actual}")