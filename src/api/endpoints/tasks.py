from typing import List, Optional, Literal
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger
from src.repositories.tasks import TaskRepository
from src.schemas.tasks import STaskAdd, STask, STaskId, STaskDelete
from src.api.dependencies import get_current_user
from src.repositories.users import UserRepository
from src.auth.auth_service import AuthService
from src.core.database import get_session


router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.post("")
async def add_task(
        title: str = Query(...),
        description: Optional[str] = Query(None),
        token: str = Depends(AuthService.get_token_from_cookie),
        session: AsyncSession = Depends(get_session)
) -> STaskId:
    payload = AuthService.decode_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await UserRepository.get_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task_data = STaskAdd(title=title, description=description)

    logger.info(f"Received task: {task_data} from user {user.user_email}")
    try:
        task_id = await TaskRepository.add_one(task_data, owner_id=user.id, session=session)
        logger.info("Creating new task")
        return STaskId(task_id=task_id)
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task with the same attributes already exists."
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )


@router.get("", response_model=List[STask])
async def get_tasks(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        name_contains:
        Optional[str] = Query(None, description="Фильтр по части имени задачи"),
        sort_by: Optional[Literal["name", "created_at"]] = Query(
            "created_at",
            description="Поле для сортировки"
        ),
        sort_desc: bool = Query(False, description="Сортировать по убыванию"),
        current_user=Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
) -> List[STask]:
    try:
        tasks = await TaskRepository.find_all(
            owner_id=current_user.id,
            session=session,
            skip=skip,
            limit=limit,
            name_contains=name_contains,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        return tasks
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't get the task list. Try again later."
        )


@router.put("/{task_id}", response_model=STask)
async def update_task(
        task_id: int,
        title: str = Query(...),
        description: Optional[str] = Query(None),
        token: str = Depends(AuthService.get_token_from_cookie),
        session: AsyncSession = Depends(get_session)
) -> STask:
    payload = AuthService.decode_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await UserRepository.get_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task_data = STaskAdd(title=title, description=description)

    try:
        updated_task = await TaskRepository.update_one(task_id, task_data, owner_id=user.id, session=session)
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IntegrityError as e:
        logger.error(f"Database integrity error while updating task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Data integrity error. Please check the entered data.")
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error while updating task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database error. Try again later.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while updating task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error has occurred. Try again later.")


@router.delete("/{task_id}", response_model=STaskDelete)
async def delete_task(
        task_id: int,
        token: str = Depends(AuthService.get_token_from_cookie),
        session: AsyncSession = Depends(get_session)
) -> STaskDelete:
    payload = AuthService.decode_token(token)
    user_email = payload.get("sub")
    if not user_email:
        logger.error(f"No cookie")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await UserRepository.get_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        result = await TaskRepository.delete_one(task_id, owner_id=user.id, session=session)
        logger.info(f"Task {task_id} deleted successfully: {result}")
        return STaskDelete(**result)
    except ValueError as e:
        logger.error(f"Task {task_id} not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IntegrityError as e:
        logger.error(f"Integrity error when deleting task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The task cannot be deleted due to data integrity limitations.")
    except SQLAlchemyError as e:
        logger.error(f"Database error when deleting task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database error. Try again later.")
    except Exception as e:
        logger.error(f"Unexpected error when deleting task {task_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error has occurred. Try again later.")
