from app.core.dependencies import get_db
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
def read_users(db=Depends(get_db)):
    # Implement logic to read users from the database
    return {"message": "List of users"}