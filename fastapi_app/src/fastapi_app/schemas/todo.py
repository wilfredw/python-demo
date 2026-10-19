"""HTTP schemas for Todo requests and responses."""

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    completed: bool = False


class TodoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=100)
    completed: bool | None = None


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool

