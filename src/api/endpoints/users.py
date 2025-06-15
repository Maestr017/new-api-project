from fastapi import APIRouter, HTTPException, Query, Response, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import Token, UserCreate
from src.auth.auth_service import auth_service
from src.repositories.users import UserRepository
from src.core.database import get_session


router = APIRouter(tags=['Пользователи'])


@router.post("/register")
async def register_user(
    user_email: str = Query(...),
    password: str = Query(...),
    is_active: bool = Query(True),
    is_superuser: bool = Query(False),
    is_verified: bool = Query(False),
    session: AsyncSession = Depends(get_session)
):
    user_data = UserCreate(
        user_email=user_email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
    existing = await UserRepository.get_by_email(user_data.user_email, session)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = auth_service.hash_password(user_data.password)
    await UserRepository.create_user(user_data.user_email, hashed, session)
    return {"msg": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_email(form_data.username, session)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = auth_service.create_token(user.user_email)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60,
        samesite="lax"
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me")
async def get_me(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    token = auth_service.get_token_from_cookie(request)
    payload = auth_service.decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await UserRepository.get_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": user.user_email}
