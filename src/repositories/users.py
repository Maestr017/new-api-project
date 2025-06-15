from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import UserOrm


class UserRepository:
    @classmethod
    async def get_by_email(cls, user_email: str, session: AsyncSession) -> UserOrm | None:
        result = await session.execute(
            select(UserOrm).where(UserOrm.user_email == user_email)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, user_email: str, hashed_password: str, session: AsyncSession) -> UserOrm:
        user = UserOrm(user_email=user_email, hashed_password=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def delete_by_email(cls, user_email: str, session: AsyncSession) -> bool:
        result = await session.execute(
            select(UserOrm).where(UserOrm.user_email == user_email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True
