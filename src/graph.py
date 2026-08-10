"""LangGraph wiring for Phase 1: Planner -> Researcher -> Writer (linear, no Critic yet)."""
from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.agents.planner import planner_node
from src.agents.researcher import researcher_node
from src.agents.writer import writer_node


def build_phase1_graph():
    graph = StateGraph(GraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()