from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.schemas.users import Token, UserCreate
from src.auth.auth_service import auth_service
from src.repositories.users import UserRepository


router = APIRouter(tags=['Пользователи'])


@router.post("/register")
async def register_user(user: Annotated[UserCreate, Depends()]):
    existing = await UserRepository.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = auth_service.hash_password(user.password)
    await UserRepository.create_user(user.email, hashed)
    return {"msg": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserRepository.get_by_email(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = auth_service.create_token(user.email)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60,
        samesite="lax"
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me")
async def get_me(request: Request):
    token = auth_service.get_token_from_cookie(request)
    payload = auth_service.decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await UserRepository.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": user.email}
