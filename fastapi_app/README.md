# FastAPI App

This demo keeps the HTTP, application, domain, and storage concerns separate.

## Run

```bash
uv run fastapi-app
```

The ASGI application is also available as `fastapi_app.main:app`.

## Structure

- `main.py` exposes one app instance per worker; `app_factory.py` assembles it.
- `controller/` contains `APIRouter` definitions and thin HTTP endpoint methods.
- `schemas/` contains Pydantic request and response contracts.
- `application/` contains Todo use cases, change events, and maps missing items to an application error.
- `domain/` contains the immutable Todo entity and repository protocol.
- `infrastructure/` contains the in-memory repository adapter and process-local WebSocket subscription manager.

The repository is intentionally in-memory for this demo. Data is process-local and is lost on restart; replace the adapter with a database-backed implementation for persistent or multi-worker deployments.

## Todo change WebSocket

Connect to `/ws/todos`. Send one JSON command per message; a connection can subscribe to multiple Todo IDs. For example, send:

```json
{"action":"subscribe","todo_id":1}
{"action":"unsubscribe","todo_id":1}
```

The server acknowledges each command with a `subscription.ack` message, for example:

```json
{"type":"subscription.ack","action":"subscribe","todo_id":1}
```

After a subscribed Todo is created, updated, or deleted, it sends `todo.created`, `todo.updated`, or `todo.deleted` with `todo_id` and a `todo` snapshot. For example:

```json
{"type":"todo.updated","todo_id":1,"todo":{"id":1,"title":"Buy milk","completed":true}}
```

Deletion events include the last Todo snapshot. Invalid commands receive a generic `invalid_command` error. Commands are limited to 4 KiB; a connection whose outbound queue exceeds 100 messages is closed with WebSocket code 1013.

Subscriptions and delivery are process-local, so clients connected to another worker will not receive these events. The current demo has no user identity or Todo ownership model; production deployments must authenticate WebSocket connections, check allowed `Origin` values, authorize access to each Todo, and rate-limit connections/commands before accepting subscriptions or publishing its data. Use a shared event broker when deploying multiple workers.
