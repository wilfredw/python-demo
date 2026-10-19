"""Application composition root."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .application.errors import TodoNotFoundError
from .controller.router import api_router
from .domain.todo_repository import TodoRepository
from .infrastructure.in_memory_todo_repository import InMemoryTodoRepository
from .infrastructure.todo_subscription_manager import TodoSubscriptionManager


def create_app(*, todo_repository: TodoRepository | None = None) -> FastAPI:
    app = FastAPI(title="Wilfred FastAPI App")
    app.state.todo_repository = (
        todo_repository
        if todo_repository is not None
        else InMemoryTodoRepository()
    )
    app.state.todo_subscription_manager = TodoSubscriptionManager()
    app.include_router(api_router)

    @app.exception_handler(TodoNotFoundError)
    async def handle_todo_not_found(
        _request: Request,
        _exc: TodoNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Todo not found"},
        )

    return app

