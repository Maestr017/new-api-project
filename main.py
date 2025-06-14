from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import sys

from src.core.database import create_tables
from src.core.logger import logger
from src.api.endpoints.tasks import router as tasks_router
from src.api.endpoints.users import router as users_router
from src.auth.middleware import AuthMiddleware

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    logger.info("База готова к работе")
    yield
    logger.info("Выключение")


app = FastAPI(lifespan=lifespan)

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

