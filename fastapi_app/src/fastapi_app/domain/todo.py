"""Domain entity for a Todo item."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Todo:
    id: int
    title: str
    completed: bool = False

