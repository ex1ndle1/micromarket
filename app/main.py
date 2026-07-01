from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import message_router
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.databases import engine, Base
from app.middleware.ip_address import RealIPMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS market"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_router)
app.add_middleware(RealIPMiddleware)