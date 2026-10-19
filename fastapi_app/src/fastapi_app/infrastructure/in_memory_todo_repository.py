"""Thread-safe in-memory repository used by this demo application."""

from dataclasses import replace
from threading import Lock

from ..domain.todo import Todo


class InMemoryTodoRepository:
    def __init__(self) -> None:
        self._items: dict[int, Todo] = {}
        self._next_id = 1
        self._lock = Lock()

    def create_todo(self, *, title: str, completed: bool) -> Todo:
        with self._lock:
            todo = Todo(id=self._next_id, title=title, completed=completed)
            self._items[todo.id] = todo
            self._next_id += 1
            return todo

    def list_todos(self, *, completed: bool | None = None) -> list[Todo]:
        with self._lock:
            items = list(self._items.values())
        if completed is None:
            return items
        return [todo for todo in items if todo.completed is completed]

    def get_todo(self, todo_id: int) -> Todo | None:
        with self._lock:
            return self._items.get(todo_id)

    def update_todo(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Todo | None:
        with self._lock:
            current = self._items.get(todo_id)
            if current is None:
                return None

            changes: dict[str, str | bool] = {}
            if title is not None:
                changes["title"] = title
            if completed is not None:
                changes["completed"] = completed

            updated = replace(current, **changes)
            self._items[todo_id] = updated
            return updated

    def delete_todo(self, todo_id: int) -> Todo | None:
        with self._lock:
            return self._items.pop(todo_id, None)

