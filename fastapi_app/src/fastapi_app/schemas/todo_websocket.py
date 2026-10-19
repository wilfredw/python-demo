"""Validated commands accepted by the Todo WebSocket endpoint."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TodoSubscriptionCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    action: Literal["subscribe", "unsubscribe"]
    todo_id: int = Field(gt=0, le=2_147_483_647)
