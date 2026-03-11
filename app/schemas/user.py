from datetime import date

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class EditNidData(BaseModel):
    name: str | None = None
    name_bn: str | None = None
    fathers_name: str | None = None
    mothers_name: str | None = None
    dob: date | None = None


class NidData(EditNidData):
    nid: int
