"""Compose routers for the application."""

from fastapi import APIRouter

from .todo_items_management import router as todo_items_router
from .todo_subscriptions import router as todo_subscriptions_router

api_router = APIRouter()
api_router.include_router(todo_items_router)
api_router.include_router(todo_subscriptions_router)

