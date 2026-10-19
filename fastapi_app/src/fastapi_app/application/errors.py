"""Application-layer exceptions translated to HTTP responses at the edge."""


class TodoNotFoundError(Exception):
    """Raised when a requested Todo does not exist."""

