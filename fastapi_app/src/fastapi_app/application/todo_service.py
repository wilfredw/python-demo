"""Todo use cases, independent of FastAPI and storage details."""

from ..domain.todo import Todo
from ..domain.todo_repository import TodoRepository
from .events import TodoChangeEvent, TodoEventPublisher
from .errors import TodoNotFoundError


class TodoService:
    def __init__(
        self,
        repository: TodoRepository,
        event_publisher: TodoEventPublisher,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    async def create_todo(self, *, title: str, completed: bool = False) -> Todo:
        todo = self._repository.create_todo(title=title, completed=completed)
        await self._event_publisher.publish(TodoChangeEvent("created", todo))
        return todo

    async def list_todos(self, *, completed: bool | None = None) -> list[Todo]:
        return self._repository.list_todos(completed=completed)

    async def get_todo(self, todo_id: int) -> Todo:
        todo = self._repository.get_todo(todo_id)
        if todo is None:
            raise TodoNotFoundError from None
        return todo

    async def update_todo(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Todo:
        todo = self._repository.update_todo(
            todo_id,
            title=title,
            completed=completed,
        )
        if todo is None:
            raise TodoNotFoundError from None
        await self._event_publisher.publish(TodoChangeEvent("updated", todo))
        return todo

    async def delete_todo(self, todo_id: int) -> None:
        todo = self._repository.delete_todo(todo_id)
        if todo is None:
            raise TodoNotFoundError from None
        await self._event_publisher.publish(TodoChangeEvent("deleted", todo))

