from fastapi import FastAPI
import uvicorn

from contextlib import asynccontextmanager

from src.core.database import create_tables
from src.core.logger import logger
from src.api.endpoints.router import router as tasks_router
from src.api.endpoints.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    logger.info("База готова к работе")
    yield
    logger.info("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(app)
