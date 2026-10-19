# Agent Diplomacy V3 Responsible AI Evaluation Plan

> **For agentic workers:** inline implementation. Run tests before and after; do not create prefilled benchmark results.

**Goal:** Add a gated synthetic benchmark and dashboard comparing No Guard, Prompt Guard, and Bounded Delegation.

**Architecture:** A separate benchmark runner loads only a synthetic JSON scenario set, calls the current compatible model client, validates structured responses, and applies existing policy functions only in Bounded Delegation mode. A local-only API gate serves actual timestamped JSON/CSV runs to a new Dashboard view; normal V2 sessions stay unchanged.

**Tech Stack:** FastAPI, Pydantic, existing DeepSeek-compatible client, Python CSV/JSON, React/Vite.

**Spec:** `docs/superpowers/specs/2026-10-17-agent-diplomacy-v3-design.md` and the active user request.

## Global Constraints
- Benchmark data must be fictional and never loaded from personal profile files.
- Guard-disabled modes require `AGENT_DIPLOMACY_ENABLE_EVALUATION=1`, `AGENT_DIPLOMACY_EVALUATION_ENV=local`, and loopback access.
- Metrics and exports must come only from actual benchmark run records; no placeholder results.
- Preserve V2 routes, architecture, DeepSeek configuration, and existing functionality.

## Review Focus
- No valid model responses: display unavailable metrics, not fabricated zero-risk claims.
- Prompt guard: do not apply policy logic beyond the prompt in this mode.
- Bounded delegation: block before shared benchmark state mutation and record approvals.
- Model output failures: record clear failed trials without adding policy events.
- Evaluation gate disabled or remote caller: deny run/results and keep normal sessions available.

### Tasks
1. Add failing tests for scenario schema/loading, action metrics, and local evaluation gate/session-mode separation; add synthetic benchmark cases.
2. Extend the existing model client with evaluation-specific prompts and usage metadata while keeping existing `generate` callers unchanged.
3. Implement the bounded 10-round synthetic runner, policy enforcement, aggregate metrics, and real JSON/CSV persistence; verify with mocked actions and model errors.
4. Add gated evaluation API endpoints and a Dashboard comparison/export view that has a no-runs empty state.
5. Add methodology and exact experiment commands; run all backend tests and frontend build.
