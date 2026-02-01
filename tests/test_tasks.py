import pytest

from src.services import tasks as tasks_module


class _DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


def _make_async_client(response):
    class _DummyClient:
        def __init__(self, *args, **kwargs):
            self.timeout = kwargs.get("timeout")
            self.last_request = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, headers):
            self.last_request = {"url": url, "json": json, "headers": headers}
            return response

    return _DummyClient


@pytest.mark.asyncio
async def test_async_external_service_example_success(monkeypatch):
    response = _DummyResponse(
        status_code=200,
        json_data={"passed": False, "score": 0.2},
        text='{"passed": false, "score": 0.2}',
    )
    monkeypatch.setattr(tasks_module.httpx, "AsyncClient", _make_async_client(response))

    result = await tasks_module.async_external_service_example(
        {"url": "https://example.test/api", "payload": {"x": 1}}
    )

    assert result.name == "async_example"
    assert result.passed is False
    assert result.details["status_code"] == 200
    assert result.details["url"] == "https://example.test/api"


@pytest.mark.asyncio
async def test_async_external_service_example_http_error_fail_on_error(monkeypatch):
    response = _DummyResponse(status_code=500, json_data={"error": "boom"}, text="boom")
    monkeypatch.setattr(tasks_module.httpx, "AsyncClient", _make_async_client(response))

    result = await tasks_module.async_external_service_example(
        {"url": "https://example.test/api", "fail_on_error": True}
    )

    assert result.name == "async_example"
    assert result.passed is False
    assert result.details["error"] == "HTTP 500"
