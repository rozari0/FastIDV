from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.database import AsyncSessionLocal
from app.models.user import User

from .config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide an async database session per request."""
    async with AsyncSessionLocal() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        id = payload.get("sub")
        print(id)

        if id is None:
            raise HTTPException(status_code=401)

    except JWTError:
        raise HTTPException(status_code=401)

    result = await db.execute(select(User).where(User.id == int(id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401)

    return user
