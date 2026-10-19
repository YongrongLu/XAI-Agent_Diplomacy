"""Validated envelopes shared by the local Hub and personal agents."""
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

MessageType = Literal['AGENT_REGISTER', 'AGENT_STATUS', 'NEGOTIATION_REQUEST', 'NEGOTIATION_ACTION',
                      'POLICY_EVENT', 'APPROVAL_REQUIRED', 'APPROVAL_DECISION', 'SESSION_COMPLETE', 'SESSION_UPDATE']


class AgentMessage(BaseModel):
    model_config = ConfigDict(extra='forbid')
    session_id: str = Field(min_length=1, max_length=128)
    message_id: str = Field(min_length=1, max_length=128)
    sender: str = Field(min_length=1, max_length=32)
    recipient: str = Field(min_length=1, max_length=32)
    type: MessageType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
