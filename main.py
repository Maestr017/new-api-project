from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import sys

from src.core.database import create_tables
from src.core.logger import logger
from src.api.endpoints.tasks import router as tasks_router
from src.api.endpoints.users import router as users_router
from src.api.endpoints.metrics import router as metrics_router
from middleware.metrics import prometheus_middleware
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


@app.get("/Health", tags=["Health-check"])
def health_check():
    return {'200': 'OK'}


exempt_paths = [
    "/",
    "/login",
    "/register",
    "/openapi.json",
    "/docs",
    "/redoc",
]

app.add_middleware(AuthMiddleware, exempt_paths=exempt_paths)
app.middleware("http")(prometheus_middleware)

app.include_router(tasks_router)
app.include_router(users_router)
app.include_router(metrics_router)
