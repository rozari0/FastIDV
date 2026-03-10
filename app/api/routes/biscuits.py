from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/biscuits",
)


@router.get("/")
async def read_biscuits(user: Annotated[User, Depends(get_current_user)]):
    if user.is_verified:
        return {"message": f"Hello {user.email}, here are your biscuits!"}
    return {"message": "Only verified users can access biscuits."}
