"""Small in-process WebSocket router. It intentionally has no profile loader."""
import asyncio
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

from .protocol import AgentMessage

AGENTS = {'alice', 'bob', 'carol'}


class HubError(RuntimeError):
    pass


class WebSocketHub:
    def __init__(self):
        self.connections = {}
        self.dashboard_clients = set()
        self.pending = {}
        self.seen = OrderedDict()

    def envelope(self, session_id, sender, recipient, kind, payload=None, correlation_id=None):
        return AgentMessage(session_id=session_id, message_id=str(uuid.uuid4()), sender=sender,
                            recipient=recipient, type=kind, timestamp=datetime.now(timezone.utc),
                            correlation_id=correlation_id, payload=payload or {})

    def statuses(self):
        return {name: ('online' if name in self.connections else 'offline') for name in sorted(AGENTS)}

    async def publish(self, data):
        dead = []
        for client in list(self.dashboard_clients):
            try:
                await client.send_json(data)
            except Exception:
                dead.append(client)
        for client in dead:
                self.dashboard_clients.discard(client)

    async def publish_session(self, session_id, public_state):
        terminal = public_state.get('status') in {'complete', 'no_agreement'}
        kind = 'SESSION_COMPLETE' if terminal else 'SESSION_UPDATE'
        message = self.envelope(session_id, 'hub', 'dashboard', kind, {'session': public_state})
        await self.publish(message.model_dump(mode='json'))

    async def register(self, websocket, agent):
        if agent not in AGENTS:
            raise HubError('Unknown agent identity')
        previous = self.connections.get(agent)
        self.connections[agent] = websocket
        if previous and previous is not websocket:
            try:
                await previous.close()
            except Exception:
                pass
        await self.publish(self.envelope('*', 'hub', 'dashboard', 'AGENT_STATUS',
            {'agent': agent, 'status': 'online', 'agents': self.statuses()} ).model_dump(mode='json'))

    async def unregister(self, websocket):
        for agent, current in list(self.connections.items()):
            if current is websocket:
                del self.connections[agent]
                await self.publish(self.envelope('*', 'hub', 'dashboard', 'AGENT_STATUS',
                    {'agent': agent, 'status': 'offline', 'agents': self.statuses()} ).model_dump(mode='json'))
                for key, pending in list(self.pending.items()):
                    future = pending['future']
                    if key[1] == agent and not future.done():
                        future.set_exception(HubError(f'{agent.title()} agent disconnected. Negotiation paused safely.'))
                break

    async def route_agent_message(self, raw, websocket):
        message = AgentMessage.model_validate(raw)
        identity = next((name for name, ws in self.connections.items() if ws is websocket), None)
        if message.type == 'AGENT_REGISTER':
            requested = message.payload.get('agent')
            if requested != message.sender or requested not in AGENTS:
                raise HubError('Registration identity mismatch')
            await self.register(websocket, requested)
            return
        if identity is None or identity != message.sender:
            raise HubError('Agent must register before sending messages')
        if message.recipient != 'hub' or message.type not in {'AGENT_STATUS', 'NEGOTIATION_ACTION', 'POLICY_EVENT', 'APPROVAL_REQUIRED', 'SESSION_COMPLETE'}:
            raise HubError('Agent message type or recipient is not allowed')
        key = (message.session_id, message.message_id)
        if key in self.seen:
            return
        self.seen[key] = True
        if len(self.seen) > 5000:
            self.seen.popitem(last=False)
        if message.correlation_id:
            pending = self.pending.get((message.correlation_id, identity))
            if pending and pending['session_id'] == message.session_id and not pending['future'].done():
                future = pending['future']
                future.set_result(message)

    async def request_agent(self, agent, session_id, kind, payload, timeout=100):
        agent_key = agent.lower()
        websocket = self.connections.get(agent_key)
        if websocket is None:
            raise HubError(f'{agent} agent is offline. Start or reconnect the agent, then resume.')
        request_id = str(uuid.uuid4())
        message = self.envelope(session_id, 'hub', agent_key, kind, payload, request_id)
        future = asyncio.get_running_loop().create_future()
        self.pending[(request_id, agent_key)] = {'session_id': session_id, 'future': future}
        try:
            await websocket.send_json(message.model_dump(mode='json'))
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError as exc:
            raise HubError('Agent request timed out. No action was applied.') from exc
        finally:
            self.pending.pop((request_id, agent_key), None)

    async def serve_agent(self, websocket):
        await websocket.accept()
        try:
            while True:
                await self.route_agent_message(await websocket.receive_json(), websocket)
        except Exception:
            await self.unregister(websocket)
            try:
                await websocket.close()
            except Exception:
                pass

    async def serve_dashboard(self, websocket):
        await websocket.accept()
        self.dashboard_clients.add(websocket)
        await websocket.send_json(self.envelope('*', 'hub', 'dashboard', 'AGENT_STATUS',
            {'agents': self.statuses()}).model_dump(mode='json'))
        try:
            while True:
                await websocket.receive_text()
        except Exception:
            self.dashboard_clients.discard(websocket)
