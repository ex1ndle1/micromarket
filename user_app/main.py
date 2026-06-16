from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.sql.functions import user
from user_app.databases import engine, Base
from user_app.routers import user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
