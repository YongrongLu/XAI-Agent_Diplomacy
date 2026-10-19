#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PIDS=()

cleanup() {
  echo "Stopping Agent Diplomacy local processes..."
  for pid in "${PIDS[@]:-}"; do kill "$pid" 2>/dev/null || true; done
  wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Missing .venv. Create it and install backend/requirements.txt first." >&2
  exit 1
fi
if [[ ! -d frontend/node_modules ]]; then
  echo "Missing frontend/node_modules. Run npm install in frontend first." >&2
  exit 1
fi
if [[ ! -f .env ]]; then
  echo "No .env found. Copy .env.example to .env and configure the model API before starting real agents." >&2
  exit 1
fi

.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000 &
PIDS+=("$!")
for attempt in {1..40}; do
  if curl -fsS http://127.0.0.1:8000/api/session >/dev/null; then break; fi
  sleep 0.25
done
if ! curl -fsS http://127.0.0.1:8000/api/session >/dev/null; then
  echo "Hub did not become ready on port 8000." >&2
  exit 1
fi

for agent in alice bob carol; do
  .venv/bin/python -m backend.agent_worker --agent "$agent" &
  PIDS+=("$!")
done
npm --prefix frontend run dev -- --host 127.0.0.1 &
PIDS+=("$!")
echo "Agent Diplomacy is starting. Dashboard: http://127.0.0.1:5173"
echo "Select Distributed V2 after the three agents report online. Press Ctrl-C to stop all four backend processes and the frontend."
while kill -0 "$HUB_PID" 2>/dev/null; do sleep 1; done
echo "The Hub exited. Stopping the remaining local processes." >&2
wait "$HUB_PID" || true
