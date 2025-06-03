from sqlalchemy import select, asc, desc
from typing import Optional
from sqlalchemy.sql import Select

from src.core.database import new_session, TaskOrm
from src.schemas.schemas import STaskAdd, STask


class TaskRepository:
    @classmethod
    async def add_one(cls, data: STaskAdd) -> int:
        async with new_session() as session:
            task_dict = data.model_dump()

            task = TaskOrm(**task_dict)
            session.add(task)
            await session.flush()
            await session.commit()
            return task.id

    @classmethod
    async def find_all(
            cls,
            skip: int = 0,
            limit: int = 10,
            name_contains: Optional[str] = None,
            sort_by: Optional[str] = "created_at",
            sort_desc: bool = False
    ) -> list[STask]:
        async with new_session() as session:
            query: Select = select(TaskOrm)

            if name_contains:
                query = query.where(TaskOrm.name.ilike(f"%{name_contains}%"))

            sort_column = getattr(TaskOrm, sort_by, None)
            if sort_column is not None:
                if sort_desc:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))

            query = query.offset(skip).limit(limit)

            result = await session.execute(query)
            task_models = result.scalars().all()
            task_schemas = [STask.model_validate(task_model) for task_model in task_models]
            return task_schemas

    @classmethod
    async def update_one(cls, task_id: int, data: STaskAdd) -> STask:
        async with new_session() as session:
            query = select(TaskOrm).where(TaskOrm.id == task_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if task is None:
                raise ValueError("Task not found")

            task.name = data.name
            task.description = data.description

            await session.commit()
            await session.refresh(task)
            return STask.model_validate(task)

    @classmethod
    async def delete_one(cls, task_id: int) -> dict:
        async with new_session() as session:
            query = select(TaskOrm).where(TaskOrm.id == task_id)
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if task is None:
                raise ValueError("Task not found")

            await session.delete(task)
            await session.commit()
            return {"ok": True, "message": f"Task {task_id} deleted"}
