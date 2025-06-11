from fastapi import Depends, HTTPException, status, Request
from jose.jwt import JWTError
from typing import Annotated

from src.repositories.tasks import TaskRepository
from src.auth.auth_service import auth_service
from src.repositories.users import UserRepository


def get_task_repo() -> TaskRepository:
    return TaskRepository()


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]


async def get_current_user(request: Request):
    token = auth_service.get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = auth_service.decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await UserRepository.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_user_by_email(email: str):
    user = await UserRepository.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
