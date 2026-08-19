
**Never commit `.env` or paste real keys anywhere public** — if a key is
ever exposed, rotate it immediately at the links above.

## Running it

```bash
# Run the full pipeline on a set of test questions
uv run python -m tests.test_phase1_e2e
```

Individual component tests:
```bash
uv run python -m tests.test_planner              # Planner only
uv run python -m tests.test_researcher            # Planner + Researcher
uv run python -m tests.test_researcher_routing    # tool-selection heuristic
uv run python -m tests.test_phase2_revision       # Critic revision loop
uv run python -m tests.test_notion_tools          # raw Notion API calls
uv run python -m tests.test_mcp_server_standalone # MCP protocol layer
```

## Known limitations

- **Groq free-tier rate limits.** The pipeline can make 8–12+ LLM calls per
  question (Planner, one extraction call per sub-question, Writer, Critic,
  plus any revision cycles). `src/llm.py` retries on HTTP 429 with backoff,
  but sustained low-RPM limits will still slow multi-question runs. Tool
  selection in the Researcher uses a cheap keyword heuristic rather than an
  LLM call specifically to reduce call volume — see the comment in
  `researcher.py` for the heuristic's known edge cases.
- **Notion tool routing is a heuristic, not learned.** Questions must contain
  a signal phrase (e.g. "my notes") to route to Notion; otherwise they go to
  web search. Misses on unusual phrasing are expected.
- **MCP server spins up a fresh subprocess per tool call** (`client.py`) —
  simple and correct, not optimized for call volume.
- **DuckDuckGo search can rate-limit or time out** under load; `search.py`
  retries with backoff and returns an empty result set (not a crash) if all
  retries fail — the Researcher then just skips that sub-question rather
  than aborting the whole run.
- **Voice I/O (Phase 4) is incomplete**: `src/voice/stt.py` exists and can
  transcribe an audio file or record from a mic (needs `libportaudio2` at
  the OS level), but it isn't called anywhere in `graph.py`, and there is no
  TTS output yet.

## Non-goals (see CHARTER.md)

No web UI, no real-time/streaming voice, only one custom MCP server, no
persisted conversation history across sessions, single-user/local only.