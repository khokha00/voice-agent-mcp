# Charter — voice-agent-mcp

## Goal
Build a voice-driven multi-agent research system: Planner → Researcher →
Critic → Writer agents (LangGraph), where the Researcher can call real
tools via MCP (web search + a custom MCP server), the Critic can send
work back for revision, and the final report is delivered as a spoken
summary.

Independent of ragstack-core (Week 1) — no shared code, no vector store,
no fixed corpus. Retrieval here is live web search + MCP tools.

## Non-goals (explicitly out of scope)
- A UI beyond CLI / simple script — no web frontend
- Real-time/streaming voice (record → transcribe → respond is fine,
  no need for live conversational turn-taking)
- More than one custom MCP server
- Persisting conversation history across sessions
- Multi-user / auth / deployment — single-user local tool

## Phased definition of done

### Phase 1 — Multi-agent core (text-only)
- [ ] Planner agent takes a typed research question and produces a plan
      (list of sub-questions or research steps)
- [ ] Researcher agent executes the plan using a web search tool, returns
      findings with source URLs attached to every claim
- [ ] Writer agent turns findings into a structured report (not just a
      dump of the Researcher's raw notes)
- [ ] Shared LangGraph state object passed cleanly between all three
      agents — no agent re-deriving context it should already have
- [ ] Runs end-to-end on at least 5 varied test questions without
      crashing or looping indefinitely

### Phase 2 — Critic + revision loop
- [ ] Critic agent checks the Writer's report against the Researcher's
      sourced findings: every non-trivial claim must trace to a source
- [ ] Critic can route back to Researcher (missing/insufficient info) OR
      to Writer (poorly phrased but well-sourced) — these are different
      failure modes and must be routed differently
- [ ] Hard cap on revision loops (e.g. max 2 cycles) to guarantee
      termination — no infinite loop risk
- [ ] Test: at least one deliberately weak/uncited draft actually gets
      sent back and improved, not just approved by default

### Phase 3 — Custom MCP server
- [ ] One custom MCP server written from scratch, 2–3 real tools (not
      stubs) against a target you pick (e.g. a notes API, task manager,
      or a small service you control)
- [ ] Researcher agent can choose between web search and the custom MCP
      tools depending on the question — not hardcoded to always use both
- [ ] Graceful handling when no tool fits the request (agent says so,
      doesn't hallucinate a tool call)
- [ ] MCP server has its own tests, independent of the agent stack

### Phase 4 — Voice I/O
- [ ] Spoken question → Whisper transcription → fed into Phase 1's
      Planner unchanged (proves the text pipeline was decoupled properly)
- [ ] Final Writer report summarized (not read verbatim — a report isn't
      speakable as-is) and sent to TTS
- [ ] Manual test: ask a question out loud, get a coherent spoken answer,
      end to end, at least 3 times with different questions
- [ ] Audio pipeline has its own fallback: if STT/TTS fails, the system
      still works in text mode rather than crashing entirely

## Key architecture decisions
- LangGraph for orchestration — explicit graph state and conditional
  edges are what make the Critic's revision routing possible; a plain
  agent loop wouldn't cleanly support "route back to a specific
  upstream agent based on failure type."
- Agents are separate LangGraph nodes with a shared, typed (Pydantic)
  state object — no agent should be passing free-text context to the
  next one when a structured field would do.
- Web search and MCP tools are both exposed to the Researcher as tools
  in the same interface — the agent shouldn't need special-case code
  per tool source.
- Text pipeline (Phases 1-3) must work completely before Phase 4 starts.
  Voice is an I/O adapter on top, not a foundation — debugging agent
  logic through an audio round-trip is slow and unreliable, so it comes
  last on purpose.

## Risks / things that could bite us
- LangGraph revision loops without a hard cap can loop indefinitely —
  cap enforced from Phase 2, not added later as a patch
- Writing a real MCP server (not just consuming one) is the least
  familiar piece here — budget extra time for Phase 3
- Whisper/TTS API costs and rate limits — check pricing before Phase 4,
  not during it
- Web search tool quality varies a lot by provider — worth testing 2-3
  search APIs early in Phase 1 rather than committing blind