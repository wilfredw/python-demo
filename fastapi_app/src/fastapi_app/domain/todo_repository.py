"""Repository contract consumed by the application layer."""

from typing import Protocol

from .todo import Todo


class TodoRepository(Protocol):
    def create_todo(self, *, title: str, completed: bool) -> Todo: ...

    def list_todos(self, *, completed: bool | None = None) -> list[Todo]: ...

    def get_todo(self, todo_id: int) -> Todo | None: ...

    def update_todo(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Todo | None: ...

    def delete_todo(self, todo_id: int) -> Todo | None: ...

