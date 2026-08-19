"""Researcher agent: for each plan step, decides whether web search, Notion
MCP tools, or nothing fits — then executes and produces sourced findings.
Tool selection uses a cheap heuristic (not an LLM call) to conserve rate-limited
API calls; only the extraction step calls the LLM."""
from src.llm import call_llm_json
from src.state import GraphState, Finding
from src.tools.search import web_search
from src.mcp_server.client import call_mcp_tool
import json

EXTRACT_SYSTEM_PROMPT = """You are a research assistant. You are given a sub-question \
and a set of source results (title, url/id, snippet/content). Extract the concrete \
facts that answer the sub-question. Only use facts actually supported by the given \
content — do not invent information.

Respond ONLY with JSON in this exact shape, no other text:
{"claims": [{"claim": "...", "source_url": "...", "source_title": "..."}, ...]}

If none of the results answer the sub-question, return {"claims": []}.
"""

# Cheap heuristic instead of an LLM router call — conserves rate-limited requests.
# Any question mentioning the user's own stuff routes to Notion; everything else
# goes to the open web.
NOTION_SIGNAL_WORDS = ("my notes", "i wrote", "i saved", "my page", "my notion")


def _pick_tool(question: str) -> str:
    q_lower = question.lower()
    if any(signal in q_lower for signal in NOTION_SIGNAL_WORDS):
        return "notion_search"
    return "web_search"


def _run_web_search(question: str) -> list[dict]:
    results = web_search(question)
    return [
        {"title": r["title"], "url": r["url"], "content": r["snippet"]}
        for r in results
    ]


def _run_notion_search(question: str) -> list[dict]:
    raw = call_mcp_tool("notion_search", {"query": question, "max_results": 5})
    try:
        pages = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return []

    out = []
    for p in pages:
        content = call_mcp_tool("notion_read_page", {"page_id": p["id"]})
        out.append({"title": p["title"], "url": p.get("url", p["id"]), "content": content or ""})
    return out


def researcher_node(state: GraphState) -> dict:
    """LangGraph node. Reads state.plan, writes state.findings."""
    all_findings: list[Finding] = []

    for step in state.plan:
        try:
            tool = _pick_tool(step.question)
            sources = _run_web_search(step.question) if tool == "web_search" else _run_notion_search(step.question)

            if not sources:
                continue

            sources_text = "\n\n".join(
                f"Title: {s['title']}\nURL/ID: {s['url']}\nContent: {s['content']}"
                for s in sources
            )
            user_prompt = f"Sub-question: {step.question}\n\nSources:\n{sources_text}"

            result = call_llm_json(EXTRACT_SYSTEM_PROMPT, user_prompt)
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