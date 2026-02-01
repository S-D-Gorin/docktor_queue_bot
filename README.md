# FastAPI TaskRunner

Small FastAPI service that runs named tasks (sync or async) and returns their results.

## Features
- Run multiple checks in one request.
- Sync tasks run in a thread pool; async tasks run directly on the event loop.
- Example sync task and async external-service task included.

## Requirements
- Python 3.11+
- Dependencies in `requirements.txt`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

Service is available at `http://localhost:8000`.

## Run with Docker
```bash
docker compose up --build
```

## API
### Health check
`GET /health`

Response:
```json
{"status": "ok"}
```

### Run tasks
`POST /api/task`

Request body:
```json
{
  "tasks": ["example", "async_example"],
  "options": {
    "example": {"params": {"data": "hello"}},
    "async_example": {
      "params": {
        "url": "https://example.com/api",
        "api_key": "secret",
        "timeout": 2.0,
        "fail_on_error": false,
        "payload": {"text": "ping"}
      }
    }
  }
}
```

Response:
```json
{
  "results": [
    {
      "name": "example",
      "passed": true,
      "details": {
        "status": "Example task executed",
        "data": "hello"
      }
    }
  ]
}
```

## Available tasks
### example (sync)
- Params: `data` (any)
- Always returns `passed: true`

### async_example (async)
Calls an external HTTP API via `httpx.AsyncClient`.
Params:
- `url` (default: `https://example.com/api`)
- `api_key` (optional, used as Bearer token)
- `timeout` (seconds, default: 2.0 or `EXTERNAL_SERVICE_TIMEOUT`)
- `fail_on_error` (boolean, default: false)
- `payload` (dict)

Environment variables:
- `EXTERNAL_SERVICE_TIMEOUT` (seconds)

## Custom tasks
Add your task function to `src/services/tasks.py` and register it in `AVAILABLE_TASKS`.

### Sync task example
```python
from typing import Dict, Any
from ..schemas import TaskResult

def my_sync_task(params: Dict[str, Any]) -> TaskResult:
    value = params.get("value")
    return TaskResult(
        name="my_sync_task",
        passed=value is not None,
        details={"value": value},
    )

AVAILABLE_TASKS["my_sync_task"] = my_sync_task
```

### Async task example
```python
from typing import Dict, Any
from ..schemas import TaskResult

async def my_async_task(params: Dict[str, Any]) -> TaskResult:
    return TaskResult(
        name="my_async_task",
        passed=True,
        details={"info": "ok"},
    )

AVAILABLE_TASKS["my_async_task"] = my_async_task
```

### Call your task
```json
{
  "tasks": ["my_sync_task"],
  "options": {
    "my_sync_task": {"params": {"value": 123}}
  }
}
```

## Tests
Run tests in the project root:
```bash
python -m pytest -q
```
