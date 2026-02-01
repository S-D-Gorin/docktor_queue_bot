import asyncio
from typing import List
from fastapi.concurrency import run_in_threadpool

from .schemas import TaskRequest, TaskResponse, TaskResult
from .services.tasks import AVAILABLE_TASKS


class TaskRunner:
    def __init__(self):
        pass

    async def run(self, req: TaskRequest) -> TaskResponse:
        tasks = []

        for task_name in req.tasks:
            task_func = AVAILABLE_TASKS.get(task_name)
            if not task_func:
                continue

            params = {}
            if req.options and task_name in req.options:
                params = req.options[task_name].params

            # если функция асинхронная — ждём её напрямую
            if asyncio.iscoroutinefunction(task_func):
                tasks.append(
                    task_func(
                        text=req.text,
                        params=params,
                    )
                )
            else:
                # синхронные проверки гоняем в threadpool, чтобы не блокировали event loop
                tasks.append(
                    run_in_threadpool(
                        task_func,
                        params=params,
                    )
                )

        results: List[TaskResult] = await asyncio.gather(*tasks)

        return TaskResponse(
            results=results,
        )
