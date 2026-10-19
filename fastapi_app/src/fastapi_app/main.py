"""ASGI entry point for the FastAPI application."""

from .app_factory import create_app

app = create_app()
