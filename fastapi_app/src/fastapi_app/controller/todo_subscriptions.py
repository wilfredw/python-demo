"""WebSocket endpoint for subscribing to Todo change events."""

import asyncio
from typing import cast

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ..infrastructure.todo_subscription_manager import (
    TodoSubscriptionManager,
)
from ..schemas.todo_websocket import TodoSubscriptionCommand

router = APIRouter(tags=["todo-events"])
_MAX_COMMAND_BYTES = 4_096


@router.websocket("/ws/todos")
async def todo_change_stream(websocket: WebSocket) -> None:
    manager = cast(
        TodoSubscriptionManager,
        websocket.app.state.todo_subscription_manager,
    )
    await websocket.accept()
    connection = manager.connect(websocket)
    sender = asyncio.create_task(manager.send_pending(websocket, connection))
    manager.enqueue(websocket, {"type": "connected"})

    try:
        while True:
            raw_command = await websocket.receive_text()
            if len(raw_command.encode("utf-8")) > _MAX_COMMAND_BYTES:
                sender.cancel()
                await asyncio.gather(sender, return_exceptions=True)
                await websocket.close(code=1009, reason="Command is too large")
                break

            try:
                command = TodoSubscriptionCommand.model_validate_json(raw_command)
            except ValidationError:
                manager.enqueue(
                    websocket,
                    {
                        "type": "error",
                        "code": "invalid_command",
                        "message": "Expected subscribe/unsubscribe and a positive todo_id.",
                    },
                )
                continue

            if command.action == "subscribe":
                manager.subscribe(websocket, command.todo_id)
            else:
                manager.unsubscribe(websocket, command.todo_id)
            manager.enqueue(
                websocket,
                {
                    "type": "subscription.ack",
                    "action": command.action,
                    "todo_id": command.todo_id,
                },
            )
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
        sender.cancel()
        await asyncio.gather(sender, return_exceptions=True)
