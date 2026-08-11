"""Critic agent: checks the draft report against sourced findings.
Routes back to Researcher (missing info) or Writer (bad phrasing), or approves."""
from src.llm import call_llm_json
from src.state import GraphState, CriticVerdict

SYSTEM_PROMPT = """You are a strict editorial critic. You are given a research \
question, a list of sourced findings, and a draft report. Judge whether the report \
is ready to publish.

Check for:
1. Every non-trivial claim in the report traces back to one of the given findings
   (no unsupported/invented claims)
2. The findings actually cover the question adequately (not too thin)
3. The report is clearly written and well-organized

Decide ONE of three outcomes:
- "approve": report is well-sourced and well-written, ship it
- "researcher": the underlying findings are missing/insufficient to properly answer
  the question — needs MORE RESEARCH, not a rewrite
- "writer": the findings are adequate but the report itself is poorly phrased,
  disorganized, or doesn't use the available findings well — needs a REWRITE, not
  more research

These are different problems — pick the one that actually matches what's wrong.

Respond ONLY with JSON in this exact shape, no other text:
{"approved": true/false, "route_to": "approve" | "researcher" | "writer", "reason": "..."}
"""


def critic_node(state: GraphState) -> dict:
    """LangGraph node. Reads draft_report + findings, writes critic_verdict."""
    findings_text = "\n".join(
        f"- {f.claim} [{f.source_url}]" for f in state.findings
    ) or "(no findings)"

    user_prompt = (
        f"Question: {state.question}\n\n"
        f"Findings:\n{findings_text}\n\n"
        f"Draft report:\n{state.draft_report}"
    )

    result = call_llm_json(SYSTEM_PROMPT, user_prompt)
    route = result.get("route_to", "approve")
    if route == "approve":
        route = "done"

    verdict = CriticVerdict(
        approved=bool(result.get("approved", False)),
        reason=result.get("reason", ""),
        route_to=route if route in ("researcher", "writer", "done") else "done",
    )
    return {"critic_verdict": verdict}