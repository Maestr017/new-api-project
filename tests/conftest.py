from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
import sys
import asyncio
from fastapi import FastAPI
from sqlalchemy.pool import NullPool

from src.models.models import Model
from src.auth.middleware import AuthMiddleware
from src.api.endpoints.tasks import router as tasks_router
from src.api.endpoints.users import router as users_router

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@host.docker.internal:5432/test_db"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
    await engine.dispose()


async def get_async_session():
    raise RuntimeError("Dependency must be overridden")


def get_app(session_dependency) -> FastAPI:
    app = FastAPI()

    from src.core.database import get_session
    app.dependency_overrides[get_session] = session_dependency

    exempt_paths = [
        "/",
        "/login",
        "/register",
        "/openapi.json",
        "/docs",
        "/redoc",
    ]
    app.add_middleware(AuthMiddleware, exempt_paths=exempt_paths)

    app.include_router(tasks_router)
    app.include_router(users_router)

    return app


@pytest_asyncio.fixture
async def async_client(test_engine):
    async_session_local = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_async_session():
        async with async_session_local() as session:
            yield session

    app = get_app(session_dependency=override_get_async_session)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
