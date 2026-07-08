
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import addresses as addresses_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="A minimal address-book API.",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(addresses_router.router, prefix="/api/v1")