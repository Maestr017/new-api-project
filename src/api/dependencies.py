from fastapi import Depends
from src.repositories.repository import TaskRepository
from typing import Annotated

def get_task_repo() -> TaskRepository:
    return TaskRepository()

TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]