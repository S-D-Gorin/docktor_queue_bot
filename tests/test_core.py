import pytest

from src.core import TaskRunner
from src.schemas import TaskRequest, TaskParams


@pytest.mark.asyncio
async def test_task_runner_runs_known_tasks_and_skips_unknown():
    runner = TaskRunner()
    req = TaskRequest(
        tasks=["example", "missing"],
        options={"example": TaskParams(params={"data": "value"})},
    )

    resp = await runner.run(req)

    assert len(resp.results) == 1
    result = resp.results[0]
    assert result.name == "example"
    assert result.passed is True
    assert result.details["data"] == "value"
