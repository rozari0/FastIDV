from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class NidData(BaseModel):
    name: str
    name_bn: str | None = None
    fathers_name: str | None = None
    mothers_name: str | None = None
    dob: str
    nid_number: str
