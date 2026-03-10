from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.jwt import create_access_token
from app.utils.security import hash_password, verify_password

router = APIRouter(
    prefix="/users",
)


@router.post("/signup")
async def signup_user(user: UserCreate, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    print(existing_user)
    if existing_user:
        return {"message": "User with this email already exists"}

    user = User(email=user.email, hashed_password=hash_password(user.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User signed up successfully"}


@router.post("/login")
async def login_user(
    user: Annotated[OAuth2PasswordRequestForm, Depends()], db=Depends(get_db)
):
    user.email = user.username
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        return {"message": "Invalid email or password"}

    if not verify_password(user.password, existing_user.hashed_password):
        return {"message": "Invalid email or password"}

    access_token = create_access_token(data={"sub": str(existing_user.id)})

    return {
        "message": "User logged in successfully",
        "access_token": access_token,
        "user_id": existing_user.id,
    }


@router.get("/me")
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        return {"message": "User not authenticated"}

    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
    }
