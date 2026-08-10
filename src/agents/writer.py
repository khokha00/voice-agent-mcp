"""Writer agent: turns sourced findings into a structured report."""
from src.llm import call_llm
from src.state import GraphState

SYSTEM_PROMPT = """You are a research report writer. Given a research question and a \
list of sourced findings, write a clear, structured report that answers the question.

Rules:
- Organize with short headings/sections, not just a flat list
- Every non-trivial claim must be attributable to one of the given findings
- Cite sources inline as [Title](url) right after the claim they support
- Do not invent facts beyond what's in the findings
- If findings are thin or contradictory, say so explicitly rather than papering over it
- Plain text / markdown output, no JSON
"""


def writer_node(state: GraphState) -> dict:
    """LangGraph node. Reads state.findings, writes state.draft_report."""
    if not state.findings:
        return {"draft_report": "No sourced findings were available to write a report."}

    findings_text = "\n".join(
        f"- {f.claim} [source: {f.source_title or f.source_url}]({f.source_url})"
        for f in state.findings
    )
    user_prompt = f"Question: {state.question}\n\nFindings:\n{findings_text}"

    report = call_llm(SYSTEM_PROMPT, user_prompt)
    return {"draft_report": report}