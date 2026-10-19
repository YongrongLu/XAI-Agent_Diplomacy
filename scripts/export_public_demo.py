"""Export the real V0 engine's fictional states for a browser-only public replay."""
import json
from copy import deepcopy
from pathlib import Path

from backend.negotiation_engine import NegotiationEngine


def snapshot(engine):
    return deepcopy({**engine.public_state(), 'mode': 'scripted'})


def export():
    engine = NegotiationEngine()
    initial = snapshot(engine)
    progression = []
    engine.start()
    progression.append(snapshot(engine))
    while engine.status == 'running':
        engine.next()
        progression.append(snapshot(engine))
    request_id = engine.pending['id']

    decisions = {}
    for choice in ('approve', 'reject'):
        branch = NegotiationEngine()
        branch.start()
        while branch.status == 'running':
            branch.next()
        branch.decide(choice, request_id)
        decided = snapshot(branch)
        branch.next()
        decisions[choice] = [decided, snapshot(branch)]

    data = {'initial': initial, 'progression': progression,
            'decisions': decisions, 'inspector': {'label': 'Fictional browser demo profiles',
                                                 'profiles': engine.inspector_state()}}
    destination = Path(__file__).resolve().parents[1] / 'frontend/src/publicDemoScenes.ts'
    destination.write_text('// Generated from backend.negotiation_engine; run python -m scripts.export_public_demo.\n'
                           'export const publicDemoScenes = '
                           + json.dumps(data, ensure_ascii=False, indent=2) + ' as const;\n', encoding='utf-8')


if __name__ == '__main__':
    export()
