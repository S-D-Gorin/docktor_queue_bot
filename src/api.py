from fastapi import APIRouter, Depends
from .schemas import TaskRequest, TaskResponse
from .core import TaskRunner

router = APIRouter()


def get_task_runner() -> TaskRunner:
    return TaskRunner()


@router.post("/task", response_model=TaskResponse)
async def run_tasks(req: TaskRequest, task_runner: TaskRunner = Depends(get_task_runner)):
    return await task_runner.run(req)