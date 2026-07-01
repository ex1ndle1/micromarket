from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os
import ssl


load_dotenv()
DB_URL = os.getenv("LOCAL_DB_URL")


connect_args = {}
if "localhost" not in DB_URL and "127.0.0.1" not in DB_URL:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context


engine = create_async_engine(
    DB_URL,
    connect_args=connect_args,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False )


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_maker() as session:
        yield session