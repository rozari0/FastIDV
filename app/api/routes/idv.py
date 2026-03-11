from json import loads
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import NidData
from app.services.llm import LLMService

upload_path = Path(settings.UPLOAD_DIR)

router = APIRouter(
    prefix="/idv",
)


@router.post("/nid")
async def upload_nid(
    user: Annotated[User, Depends(get_current_user)],
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    llm: Annotated[LLMService, Depends()],
) -> NidData:
    upload_nid_dir = upload_path / str(user.id)
    upload_nid_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / str(user.id) / ("nid." + file.filename.split(".")[-1])
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    user.nid_path = str(file_path)

    ocr_result_raw = await llm.process_image(str(file_path))
    ocr_result = await llm.process_nid(
        ocr_result_raw,
        schema=NidData.model_json_schema(),
    )

    db.add(user)
    await db.commit()
    return loads(ocr_result)
