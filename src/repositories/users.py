from sqlalchemy import select

from src.core.database import new_session
from src.models.users import UserOrm


class UserRepository:
    @classmethod
    async def get_by_email(cls, email: str) -> UserOrm | None:
        async with new_session() as session:
            result = await session.execute(select(UserOrm).where(UserOrm.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, email: str, hashed_password: str) -> UserOrm:
        async with new_session() as session:
            user = UserOrm(email=email, hashed_password=hashed_password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
