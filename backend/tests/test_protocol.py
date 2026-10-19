import pytest
from pydantic import ValidationError

from backend.protocol import AgentMessage


def test_agent_message_requires_session_id_message_id_sender_recipient_type_timestamp():
    message = AgentMessage.model_validate({
        'session_id': 's1', 'message_id': 'm1', 'sender': 'alice',
        'recipient': 'hub', 'type': 'AGENT_REGISTER',
        'timestamp': '2026-10-17T12:00:00Z', 'payload': {},
    })
    assert message.type == 'AGENT_REGISTER'


def test_agent_message_rejects_unknown_type_and_missing_required_fields():
    with pytest.raises(ValidationError):
        AgentMessage.model_validate({'session_id': 's1', 'message_id': 'm1', 'sender': 'alice',
                                     'recipient': 'hub', 'type': 'PRIVATE_PROFILE',
                                     'timestamp': '2026-10-17T12:00:00Z'})
    with pytest.raises(ValidationError):
        AgentMessage.model_validate({'session_id': 's1', 'sender': 'alice', 'recipient': 'hub',
                                     'type': 'AGENT_REGISTER', 'timestamp': '2026-10-17T12:00:00Z'})
