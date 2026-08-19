"""Planner agent: turns a raw question into a structured research plan."""
from src.llm import call_llm_json
from src.state import GraphState, ResearchStep

SYSTEM_PROMPT = """You are a research planner. Given a research question, break it \
down into 2-3 concrete, independently-answerable sub-questions (no more than 3) \
that together would let someone write a well-sourced report answering the original \
question.

Respond ONLY with JSON in this exact shape, no other text:
{"sub_questions": ["question 1", "question 2", ...]}
"""


def planner_node(state: GraphState) -> dict:
    """LangGraph node. Reads state.question, writes state.plan."""
    result = call_llm_json(SYSTEM_PROMPT, state.question)
    sub_questions = result.get("sub_questions", [])

    if not sub_questions:
        # Fallback: treat the original question as the single research step
        sub_questions = [state.question]

    plan = [ResearchStep(question=q) for q in sub_questions]
    return {"plan": plan}