from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    completed: bool = False

class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    completed: bool | None = None

class Todo(TodoCreate):
    id: int

db: dict[int, Todo] = {}
next_id = 1

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    global next_id
    todo = Todo(id=next_id, **payload.model_dump())
    db[next_id] = todo
    next_id += 1
    return todo

@app.get("/todos/", response_model=list[Todo])
def list_todos(completed: bool | None = None):
    todos = list(db.values())
    if completed is not None:
        todos = [t for t in todos if t.completed == completed]
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    if todo_id not in db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db[todo_id]

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate):
    if todo_id not in db:
        raise HTTPException(status_code=404, detail="Todo not found")

    stored = db[todo_id]
    update_data = payload.model_dump(exclude_unset=True)
    updated = stored.model_copy(update=update_data)
    db[todo_id] = updated
    return updated

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todo_id not in db:
        raise HTTPException(status_code=404, detail="Todo not found")
    del db[todo_id]