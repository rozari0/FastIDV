from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide an async database session per request."""
    async with AsyncSessionLocal() as session:
        yield session