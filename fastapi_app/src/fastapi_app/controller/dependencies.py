"""FastAPI dependencies used by HTTP controllers."""

from typing import cast

from fastapi import Request

from ..application.todo_service import TodoService
from ..domain.todo_repository import TodoRepository
from ..infrastructure.todo_subscription_manager import TodoSubscriptionManager


def get_todo_service(request: Request) -> TodoService:
    """Build a request-scoped service around this app's repository."""
    repository = cast(TodoRepository, request.app.state.todo_repository)
    publisher = cast(
        TodoSubscriptionManager,
        request.app.state.todo_subscription_manager,
    )
    return TodoService(repository, publisher)

