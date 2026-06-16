from fastapi import FastAPI
from app.routers import message_router
from contextlib import asynccontextmanager
from app.databases import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(message_router)
