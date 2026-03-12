from pathlib import Path
from pprint import pprint as print
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.models.user import NIDData, User
from app.schemas.user import EditNidData, NidData
from app.services.deepface import DeepfaceService
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

    user.nid_data = None
    await db.flush()

    nid = NIDData(
        dob=NIDData.string_to_date(ocr_result.get("dob")),
        name=ocr_result.get("name"),
        name_bn=ocr_result.get("name_bn"),
        fathers_name=ocr_result.get("fathers_name"),
        mothers_name=ocr_result.get("mothers_name"),
        nid=int(ocr_result.get("nid")),
    )

    user.nid_data = nid
    db.add(user)
    await db.commit()
    return nid


@router.put("/nid")
async def edit_nid(
    user: Annotated[User, Depends(get_current_user)],
    data: EditNidData,
    db: Annotated[Session, Depends(get_db)],
) -> NidData:
    stmt = select(User).options(selectinload(User.nid_data)).where(User.id == user.id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    if not user.nid_data:
        raise HTTPException(status_code=404, detail="No NID data found for the user")

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(user.nid_data, key, value)

    db.add(user)
    await db.commit()
    return user.nid_data


@router.get("/nid")
async def get_nid(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NidData:
    stmt = select(User).options(selectinload(User.nid_data)).where(User.id == user.id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    if not user.nid_data:
        raise HTTPException(status_code=404, detail="No NID data found for the user")
    return user.nid_data


@router.post("/verify")
async def verify_face(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    deepface: Annotated[DeepfaceService, Depends()],
    file: UploadFile,
) -> bool:
    stmt = select(User).options(selectinload(User.nid_data)).where(User.id == user.id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    if not user.nid_path:
        raise HTTPException(status_code=404, detail="No NID found for this account.")

    upload_face_dir = upload_path / str(user.id)
    upload_face_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_face_dir / ("face." + file.filename.split(".")[-1])
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    result = await deepface.verify_face(user.nid_path, str(file_path))

    return result.get("verified", False)
