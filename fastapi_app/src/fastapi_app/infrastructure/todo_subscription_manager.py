"""Process-local WebSocket subscriptions for Todo change events."""

import asyncio
from dataclasses import asdict, dataclass, field

from fastapi import WebSocket

from ..application.events import TodoChangeEvent

_OUTBOUND_QUEUE_SIZE = 100


@dataclass(slots=True)
class _Connection:
    subscriptions: set[int] = field(default_factory=set)
    outbound: asyncio.Queue[dict[str, object]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=_OUTBOUND_QUEUE_SIZE)
    )
    slow_consumer: bool = False


class TodoSubscriptionManager:
    """Fan out Todo events to subscribed connections in this app process."""

    def __init__(self) -> None:
        self._connections: dict[WebSocket, _Connection] = {}
        self._subscribers: dict[int, set[WebSocket]] = {}

    def connect(self, websocket: WebSocket) -> _Connection:
        connection = _Connection()
        self._connections[websocket] = connection
        return connection

    def subscribe(self, websocket: WebSocket, todo_id: int) -> None:
        connection = self._connections.get(websocket)
        if connection is None:
            return
        connection.subscriptions.add(todo_id)
        self._subscribers.setdefault(todo_id, set()).add(websocket)

    def unsubscribe(self, websocket: WebSocket, todo_id: int) -> None:
        connection = self._connections.get(websocket)
        if connection is None:
            return
        connection.subscriptions.discard(todo_id)
        subscribers = self._subscribers.get(todo_id)
        if subscribers is not None:
            subscribers.discard(websocket)
            if not subscribers:
                self._subscribers.pop(todo_id, None)

    def enqueue(self, websocket: WebSocket, message: dict[str, object]) -> None:
        connection = self._connections.get(websocket)
        if connection is None or connection.slow_consumer:
            return
        try:
            connection.outbound.put_nowait(message)
        except asyncio.QueueFull:
            connection.slow_consumer = True

    async def send_pending(
        self,
        websocket: WebSocket,
        connection: _Connection,
    ) -> None:
        """Be the only task that writes data or closes this WebSocket."""
        while True:
            if connection.slow_consumer:
                await websocket.close(code=1013, reason="Consumer is too slow")
                return
            message = await connection.outbound.get()
            await websocket.send_json(message)

    async def publish(self, event: TodoChangeEvent) -> None:
        message: dict[str, object] = {
            "type": f"todo.{event.kind}",
            "todo_id": event.todo.id,
            "todo": asdict(event.todo),
        }
        for websocket in tuple(self._subscribers.get(event.todo.id, ())):
            self.enqueue(websocket, message)

    def disconnect(self, websocket: WebSocket) -> None:
        connection = self._connections.pop(websocket, None)
        if connection is None:
            return
        for todo_id in connection.subscriptions:
            subscribers = self._subscribers.get(todo_id)
            if subscribers is None:
                continue
            subscribers.discard(websocket)
            if not subscribers:
                self._subscribers.pop(todo_id, None)
