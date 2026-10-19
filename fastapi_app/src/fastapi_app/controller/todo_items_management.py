"""HTTP endpoints for managing Todo items."""

from fastapi import APIRouter, Depends, status

from ..application.todo_service import TodoService
from ..domain.todo import Todo
from ..schemas.todo import TodoCreate, TodoRead, TodoUpdate
from .dependencies import get_todo_service

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post(
    "/",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    payload: TodoCreate,
    service: TodoService = Depends(get_todo_service),
) -> Todo:
    return await service.create_todo(
        title=payload.title,
        completed=payload.completed,
    )


@router.get("/", response_model=list[TodoRead])
async def list_todos(
    completed: bool | None = None,
    service: TodoService = Depends(get_todo_service),
) -> list[Todo]:
    return await service.list_todos(completed=completed)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> Todo:
    return await service.get_todo(todo_id)


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
) -> Todo:
    return await service.update_todo(
        todo_id,
        title=payload.title,
        completed=payload.completed,
    )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> None:
    await service.delete_todo(todo_id)
