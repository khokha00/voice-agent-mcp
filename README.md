# voice-agent-mcp

A multi-agent research assistant: give it a question, a LangGraph pipeline of
**Planner → Researcher → Writer → Critic** agents investigates it using real
tools — live web search and a custom MCP server for personal Notion notes —
and produces a structured, sourced report. A revision loop lets the Critic
send weak or uncited work back for another pass, with a hard cap so it can't
loop forever.

Originally scoped to add voice input/output (Whisper STT → pipeline → TTS)
as a fourth phase; the text pipeline (Phases 1–3) is complete, tested, and
the current state of the project. Voice I/O code exists but is **unwired
and untested** — see [Status](#status) below.

## What it does