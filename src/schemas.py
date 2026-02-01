from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TaskParams(BaseModel):
    params: Dict[str, Any] = {}


class TaskRequest(BaseModel):
    tasks: List[str]
    options: Optional[Dict[str, TaskParams]] = None

class TaskResult(BaseModel):
    name: str
    passed: bool
    details: Dict[str, Any] = {}


class TaskResponse(BaseModel):
    results: List[TaskResult]