"""Researcher agent: executes each plan step via web search, produces
sourced findings. Every claim must carry a source_url (charter requirement)."""
from src.llm import call_llm_json
from src.state import GraphState, Finding
from src.tools.search import web_search

SYSTEM_PROMPT = """You are a research assistant. You are given a sub-question and a \
set of web search results (title, url, snippet). Extract the concrete facts that \
answer the sub-question. Only use facts actually supported by the snippets — do not \
invent information.

Respond ONLY with JSON in this exact shape, no other text:
{"claims": [{"claim": "...", "source_url": "...", "source_title": "..."}, ...]}

If none of the results answer the sub-question, return {"claims": []}.
"""


def researcher_node(state: GraphState) -> dict:
    """LangGraph node. Reads state.plan, writes state.findings."""
    all_findings: list[Finding] = []

    for step in state.plan:
        try:
            results = web_search(step.question)
            if not results:
                continue

            results_text = "\n\n".join(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
                for r in results
            )
            user_prompt = f"Sub-question: {step.question}\n\nSearch results:\n{results_text}"

            result = call_llm_json(SYSTEM_PROMPT, user_prompt)
            for c in result.get("claims", []):
                if c.get("claim") and c.get("source_url"):
                    all_findings.append(Finding(
                        claim=c["claim"],
                        source_url=c["source_url"],
                        source_title=c.get("source_title", ""),
                    ))
        except Exception as e:
            print(f"  [researcher: skipping step {step.question!r} — {e}]")
            continue

    return {"findings": all_findings}