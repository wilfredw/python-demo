"""Application events published after Todo state changes."""

from dataclasses import dataclass
from typing import Literal, Protocol

from ..domain.todo import Todo


@dataclass(frozen=True, slots=True)
class TodoChangeEvent:
    kind: Literal["created", "updated", "deleted"]
    todo: Todo


class TodoEventPublisher(Protocol):
    async def publish(self, event: TodoChangeEvent) -> None: ...
