# research-agent-mcp

A multi-agent research assistant. Give it a question, and a LangGraph pipeline
of **Planner → Researcher → Writer → Critic** agents investigates it using
real tools — live web search and a custom MCP server for personal Notion
notes — and produces a structured, sourced report. A revision loop lets the
Critic send weak or uncited work back for another pass, capped so it always
terminates.

## How it works

```
question
   │
   ▼
Planner    ──▶ breaks the question into 2–3 sub-questions
   │
   ▼
Researcher ──▶ for each sub-question, searches the web or Notion
   │           (via a custom MCP server) and extracts sourced claims
   ▼
Writer     ──▶ turns findings into a structured report
   │
   ▼
Critic     ──▶ approves, or routes back to Researcher (thin findings)
   │           or Writer (poor phrasing) — max 2 revision cycles
   ▼
final report
```

## Stack

- **LangGraph** — agent orchestration and shared state
- **Groq** — LLM inference (OpenAI-compatible REST API)
- **`ddgs`** — free web search
- **MCP** (`mcp[cli]`) — custom server exposing Notion as agent tools
- **Notion API** — personal notes, via the custom MCP server
- **Pydantic** — shared `GraphState` schema
- **uv** — dependency management

## Project structure

```
voice-agent-mcp/
├── CHARTER.md
├── .env.example
├── src/
│   ├── state.py
│   ├── llm.py
│   ├── graph.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   └── critic.py
│   ├── tools/
│   │   └── search.py
│   └── mcp_server/
│       ├── notion_tools.py
│       ├── server.py
│       └── client.py
└── tests/
```

## Setup

```bash
uv sync
cp .env.example .env
```

Fill in `.env`:
```
GROQ_API_KEY=...              # console.groq.com/keys
GROQ_MODEL=openai/gpt-oss-120b
NOTION_API_KEY=...             # notion.so/my-integrations
NOTION_PARENT_PAGE_ID=...      # page must be shared with your integration
```

Never commit `.env` or share real keys — rotate immediately if one leaks.

## Running it

```bash
uv run python -m tests.test_phase1_e2e        # full pipeline, 5 questions
uv run python -m tests.test_planner
uv run python -m tests.test_researcher
uv run python -m tests.test_researcher_routing
uv run python -m tests.test_phase2_revision
uv run python -m tests.test_notion_tools
uv run python -m tests.test_mcp_server_standalone
```



