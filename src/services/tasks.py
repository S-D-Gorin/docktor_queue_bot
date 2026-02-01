from typing import Dict, Any
from ..schemas import TaskResult
import httpx
import os
import logging

logger = logging.getLogger(__name__)

AVAILABLE_TASKS = {}

def example_task(params: Dict[str, Any]) -> TaskResult:
    data = params.get("data", False)

    return TaskResult(
        name="example",
        passed=True,
        details={"status": "Example task executed", "data": data},
    )
AVAILABLE_TASKS["example"] = example_task

# Пример асинхронной проверки, которая обращается к внешнему сервису
async def async_external_service_example(params: Dict[str, Any]) -> TaskResult:
    """
    Асинхронная проверка через внешний сервис.

    Поддерживает параметры:
    - url: URL API
    - api_key: ключ авторизации
    - timeout: таймаут в секундах
    - fail_on_error: считать ли ошибку спамом (по умолчанию False)
    - payload: дополнительный payload ( dict )
    """

    # Параметры + env
    url = params.get("url") or "https://example.com/api"
    api_key = params.get("api_key") or ""
    fail_on_error = bool(params.get("fail_on_error", False))

    # Конвертация timeout
    try:
        timeout_str = os.getenv("EXTERNAL_SERVICE_TIMEOUT")
        if timeout_str:
            timeout = float(timeout_str)
        else:
            timeout = float(params.get("timeout", 2.0))
    except (ValueError, TypeError):
        logger.warning("Invalid timeout value, using default 2.0")
        timeout = 2.0

    # Подготавливаем payload (без мутации исходного словаря)
    raw_payload = params.get("payload") or {}
    payload: Dict[str, Any] = dict(raw_payload)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "TaskRunner/1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)

        if resp.status_code == 200:
            # Пытаемся разобрать JSON
            try:
                data = resp.json()
            except ValueError as exc:
                details = {
                    "url": url,
                    "error": f"Invalid JSON in response: {exc}",
                    "status_code": resp.status_code,
                    "request": payload,
                    "response": resp.text[:200] if resp.text else "",
                }
                return TaskResult(
                    name="async_example",
                    passed=not fail_on_error,
                    score=0.0,
                    details=details,
                )

            # Предполагаемый формат ответа
            passed = bool(data.get("passed", True))
            score = float(data.get("score", 0.0))

            details = {
                "url": url,
                "status_code": resp.status_code,
                "request": payload,
                "response": resp.text[:200] if resp.text else "",
            }

            return TaskResult(
                name="async_example",
                passed=passed,
                details=details,
            )

        else:
            # HTTP-ошибки
            details = {
                "url": url,
                "error": f"HTTP {resp.status_code}",
                "status_code": resp.status_code,
                "request": payload,
                "response": resp.text[:200] if resp.text else "",
            }

            return TaskResult(
                name="async_example",
                passed=not fail_on_error,
                details=details,
            )

    except httpx.RequestError as exc:
        # Сетевые ошибки
        error_details: Dict[str, Any] = {
            "url": url,
            "request": payload,
            "error": str(exc),
        }
        error_details["timeout"] = timeout

        if isinstance(exc, httpx.ConnectTimeout):
            error_details["type"] = "connection_timeout"
        elif isinstance(exc, httpx.ReadTimeout):
            error_details["type"] = "read_timeout"
        elif isinstance(exc, httpx.ConnectError):
            error_details["type"] = "connection_error"

        return TaskResult(
            name="async_example",
            passed=not fail_on_error,
            details=error_details,
        )

    except Exception as exc:
        # Любые другие ошибки
        details = {
            "url": url,
            "request": payload,
            "timeout": timeout,
            "error": f"Unexpected error: {exc}",
        }
        return TaskResult(
            name="async_example",
            passed=not fail_on_error,
            details=details,
        )
    
AVAILABLE_TASKS["async_example"] = async_external_service_example
