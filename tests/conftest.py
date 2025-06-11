import pytest
from jose import jwt
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime, timedelta

from src.schemas.users import UserCreate
from src.schemas.tasks import STaskAdd
from src.models.models import UserOrm, Model
from src.repositories.users import UserRepository
from src.repositories.tasks import TaskRepository
from src.auth.auth_service import auth_service
from src.core.config import settings


TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest.fixture
def test_user_data():
    return UserCreate(
        email="test@example.com",
        password="securepassword123",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )


@pytest.fixture
async def created_user(test_user_data: UserCreate):
    existing = await UserRepository.get_by_email(test_user_data.email)
    if existing:
        await UserRepository.delete_by_email(test_user_data.email)

    hashed_password = auth_service.hash_password(test_user_data.password)
    user_id = await UserRepository.create_user(test_user_data.email, hashed_password)
    user = await UserRepository.get_by_email(test_user_data.email)
    return user


@pytest.fixture
async def access_token(created_user: UserOrm) -> str:
    return auth_service.create_token(created_user.email)


@pytest.fixture
def expired_token(created_user: UserOrm) -> str:
    return jwt.encode(
        {"sub": created_user.email, "exp": datetime.utcnow() - timedelta(seconds=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


@pytest.fixture
def test_task_data() -> STaskAdd:
    return STaskAdd(name="Test Task", description="Test Description")


@pytest.fixture
async def created_task(test_task_data: STaskAdd, created_user: UserOrm):
    task_id = await TaskRepository.add_one(test_task_data, owner_id=created_user.id)
    task = await TaskRepository.get_by_id(task_id, owner_id=created_user.id)
    yield task
    await TaskRepository.delete_one(task_id, owner_id=created_user.id)
