from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.user import User

upload_path = Path(settings.UPLOAD_DIR)

router = APIRouter(
    prefix="/idv",
)


@router.post("/nid")
async def upload_nid(
    user: Annotated[User, Depends(get_current_user)],
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
):
    upload_nid_dir = upload_path / str(user.id)
    upload_nid_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / str(user.id) / ("nid." + file.filename.split(".")[-1])
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    user.nid_path = str(file_path)
    db.add(user)
    await db.commit()
    return {"message": f"{file_path}"}
