# Agent Diplomacy V2 Implementation Plan

> **For agentic workers:** inline execution; preserve the V1 state machine and keep changes incremental.

**Goal:** Run a Hub and three local personal-agent workers that negotiate using the existing policy boundaries and dashboard.

**Architecture:** The Hub routes validated, session-scoped WebSocket envelopes and contains no private profiles. Each worker loads exactly one profile, calls the existing DeepSeek-compatible model client, enforces its local policy, and returns structured decisions to the existing `LiveNegotiationEngine` coordinator. V1 remains available.

**Tech Stack:** Python, FastAPI, Pydantic, WebSocket, React/Vite, pytest.

**Spec:** User-provided Agent Diplomacy V2 requirements in the active task.

## Global Constraints
- Run four local processes on one Mac; do not claim OS-level isolation.
- Keep the existing session/proposal coordinator, dashboard design, DeepSeek client, and V0 scripted fallback.
- Hub must not load private profiles; no private profile data in session API or public logs.
- Policy checks precede public actions; approval is exact, session-bound, and one-time.
- No booking/payment; max 10 rounds; inspector requires explicit local debug enablement.

## Review Focus
- Agent disconnect during an RPC: fail closed and pause without applying action.
- Duplicate/stale approval or message IDs: reject without repeated side effects.
- Malformed or unsafe worker output: validate and expose only trusted templates.
- Local worker profile ownership: reject mismatched agent startup/profile access.
- Inspector/session API: no private data unless explicitly enabled locally.

### Tasks
1. Add protocol and Hub tests, then message schemas and WebSocket routing with deduplication/reconnect state.
2. Add independent worker CLI, local policy checks, structured public templates, and mocked worker tests.
3. Adapt `LiveNegotiationEngine` through an injectable remote client; preserve coordinator and V1 path; test local profile isolation/approval/disconnect.
4. Add distributed API mode, WebSocket dashboard feed, inspector gate, and minimal UI status/mode support.
5. Add one-command launcher, architecture diagram, README setup/operations, then run all tests and frontend build.
