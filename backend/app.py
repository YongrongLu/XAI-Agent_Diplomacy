from typing import Literal
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .negotiation_engine import NegotiationEngine
from .live_engine import LiveNegotiationEngine
from .hub import WebSocketHub
from .hub_client import HubAgentClient
from .evaluation import EvaluationRunner, evaluation_access_allowed, latest_result
from pathlib import Path

@asynccontextmanager
async def lifespan(_app):
    hub.loop = asyncio.get_running_loop()
    yield


app = FastAPI(title='Agent Diplomacy V2', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
                   allow_origin_regex=r'^https?://(localhost|127\.0\.0\.1):517[0-9]+$',
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])
engine = NegotiationEngine()
mode = 'scripted'
hub = WebSocketHub()


class DecisionBody(BaseModel):
    choice: Literal['approve', 'reject']


class ResetBody(BaseModel):
    mode: Literal['scripted', 'live', 'distributed'] | None = None


class EvaluationBody(BaseModel):
    repetitions: int = 1
    max_rounds: int = 10
    max_model_calls: int | None = None
    max_total_tokens: int | None = None
    approval_simulation: Literal['approve', 'reject', 'scenario_defined'] | None = None
    scenario_ids: list[str] | None = None
    goal_conditions: list[Literal['balanced', 'high_pressure', 'extreme']] | None = None


def state():
    result = engine.public_state()
    result['mode'] = mode
    if mode == 'scripted':
        result.update(round=None, max_rounds=None, error=None)
    return result


def push_distributed_state(result):
    if mode == 'distributed' and hub.loop and hub.loop.is_running():
        asyncio.run_coroutine_threadsafe(hub.publish_session(engine.session_id, result), hub.loop)


@app.get('/api/session')
def session():
    return state()


@app.post('/api/session/reset')
def reset(body: ResetBody | None = None):
    global engine, mode
    selected = body.mode if body and body.mode else mode
    mode = selected
    if mode == 'live':
        engine = LiveNegotiationEngine()
    elif mode == 'distributed':
        client = HubAgentClient(hub, hub.loop, float(os.getenv('AGENT_DIPLOMACY_AGENT_TIMEOUT_SECONDS', '120')))
        engine = LiveNegotiationEngine(client=client, distributed=True, hub=hub)
    else:
        engine = NegotiationEngine()
    return state()


@app.post('/api/session/start')
def start():
    engine.start()
    result = state()
    push_distributed_state(result)
    return result


@app.post('/api/session/next')
def next_step():
    engine.next()
    result = state()
    push_distributed_state(result)
    return result


@app.post('/api/approvals/{request_id}/decide')
def decide(request_id: str, body: DecisionBody):
    result = engine.decide(body.choice, request_id)
    if 'error' in result:
        raise HTTPException(409, result['error'])
    public = state()
    push_distributed_state(public)
    return public


@app.get('/api/inspector')
def inspector(request: Request):
    if os.getenv('AGENT_DIPLOMACY_ENABLE_INSPECTOR', '').lower() not in {'1', 'true', 'yes'}:
        raise HTTPException(404, 'Inspector is disabled. Set AGENT_DIPLOMACY_ENABLE_INSPECTOR=1 for local demo/debug mode.')
    host = request.client.host if request.client else ''
    if host not in {'127.0.0.1', '::1', 'testclient'}:
        raise HTTPException(403, 'Inspector is available only to local clients.')
    if mode == 'distributed':
        raise HTTPException(404, 'Private profiles are held by their local agents and are not available through the Hub.')
    return {'label': 'Owner / Demo Inspector — fictional source data, never sent in negotiation events',
            'profiles': engine.inspector_state()}


def require_evaluation_access(request: Request):
    host = request.client.host if request.client else ''
    if not evaluation_access_allowed(host, os.getenv('AGENT_DIPLOMACY_ENABLE_EVALUATION'),
                                     os.getenv('AGENT_DIPLOMACY_EVALUATION_ENV')):
        raise HTTPException(404, 'Evaluation is disabled. Enable it only for local synthetic research.')


def evaluation_results_dir():
    return Path(os.getenv('AGENT_DIPLOMACY_EVALUATION_RESULTS_DIR', 'evaluation/results'))


@app.get('/api/evaluation/status')
def evaluation_status(request: Request):
    host = request.client.host if request.client else ''
    enabled = evaluation_access_allowed(host, os.getenv('AGENT_DIPLOMACY_ENABLE_EVALUATION'),
                                        os.getenv('AGENT_DIPLOMACY_EVALUATION_ENV'))
    return {'enabled': enabled}


@app.post('/api/evaluation/run')
async def run_evaluation(request: Request, body: EvaluationBody | None = None):
    require_evaluation_access(request)
    try:
        options = body.model_dump() if body else {}
        return await run_in_threadpool(EvaluationRunner(output_dir=evaluation_results_dir(), **options).run)
    except Exception as exc:
        raise HTTPException(502, f'Evaluation failed safely: {type(exc).__name__}. No benchmark result was saved.')


@app.post('/api/evaluation/estimate')
def estimate_evaluation(request: Request, body: EvaluationBody):
    require_evaluation_access(request)
    try:
        runner = EvaluationRunner(output_dir=evaluation_results_dir(), **body.model_dump())
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    conditions = len(runner.goal_conditions) * 3
    planned_runs = len(runner.scenarios) * runner.repetitions * conditions
    return {'planned_case_runs': planned_runs, 'maximum_calls_without_budget': planned_runs * runner.max_rounds,
            'global_model_call_cap': runner.max_model_calls,
            'global_reported_token_cap': runner.max_total_tokens,
            'scenario_count': len(runner.scenarios), 'repetitions': runner.repetitions,
            'conditions': conditions, 'paid_calls_started': False}


@app.get('/api/evaluation/latest')
def evaluation_latest(request: Request):
    require_evaluation_access(request)
    return {'run': latest_result(evaluation_results_dir())}


@app.get('/api/evaluation/export/{format}')
def evaluation_export(format: str, request: Request):
    require_evaluation_access(request)
    result = latest_result(evaluation_results_dir())
    if not result:
        raise HTTPException(404, 'No benchmark run is available yet.')
    filename = result.get('artifacts', {}).get(format)
    if not filename:
        raise HTTPException(422, 'Unsupported export format for this run.')
    path = (evaluation_results_dir() / filename).resolve() if filename else None
    root = evaluation_results_dir().resolve()
    if not path or path.parent != root or not path.is_file():
        raise HTTPException(404, 'Benchmark artifact is unavailable.')
    media = 'image/svg+xml' if format.endswith('_svg') else 'image/png' if format.startswith('figure') else 'text/markdown' if format == 'md' else 'application/json' if format == 'json' else 'text/csv'
    return FileResponse(path, filename=path.name, media_type=media)


@app.websocket('/ws/agents')
async def agent_socket(websocket: WebSocket):
    await hub.serve_agent(websocket)


@app.websocket('/ws/dashboard')
async def dashboard_socket(websocket: WebSocket):
    await hub.serve_dashboard(websocket)
