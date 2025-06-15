from fastapi import Depends, HTTPException, status, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.tasks import TaskRepository
from src.auth.auth_service import auth_service
from src.repositories.users import UserRepository
from src.core.database import get_session


def get_task_repo() -> TaskRepository:
    return TaskRepository()


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]


async def get_current_user(request: Request, session: AsyncSession = Depends(get_session)):
    token = auth_service.get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = auth_service.decode_token(token)
    user_email: str = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await UserRepository.get_by_email(user_email, session=session)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
