import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from redis import asyncio as aioredis
from alembic import command
from alembic.config import Config

from src.api.main import app
from src.infrastructure.db.session import get_db, get_database_url
from src.infrastructure.redis.client import get_redis


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    """Run Alembic migrations once before the entire test session."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


# ── Database ──────────────────────────────────────────────────────────────────
# NullPool disables connection caching entirely — every use opens and closes
# a fresh connection in the *current* event loop, eliminating cross-loop errors.
_test_engine = create_async_engine(
    get_database_url(),
    poolclass=NullPool,
    future=True,
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def _override_get_db():
    """Replaces the app's get_db so requests also use the NullPool engine."""
    async with _TestSessionLocal() as session:
        yield session


# ── Redis ─────────────────────────────────────────────────────────────────────
# Same problem as asyncpg: redis.asyncio's connection pool caches connections
# bound to the event loop of the test that first used them. The next test runs
# in a different loop context and gets a stale connection → crash.
# Fix: create a fresh Redis client per request and close it when done.
# No cached connections = no cross-loop mismatch.

def _redis_url() -> str:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    return f"redis://{host}:{port}"


async def _override_get_redis():
    """Fresh Redis client per request — no cross-loop connection pool caching."""
    r = aioredis.from_url(
        _redis_url(),
        password=os.getenv("REDIS_PASS"),
        decode_responses=True,
    )
    try:
        yield r
    finally:
        await r.aclose()


# Apply dependency overrides globally for all tests.
app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_redis] = _override_get_redis


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Truncate all tables in dependency order before each test."""
    async with _TestSessionLocal() as session:
        await session.execute(text("DELETE FROM bids"))
        await session.execute(text("DELETE FROM auctions"))
        await session.execute(text("DELETE FROM products"))
        await session.commit()
    yield


@pytest_asyncio.fixture
async def client():
    """AsyncClient wired to the FastAPI app via ASGI transport."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
