from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserAuth(UserCreate):
    pass


class UserInDBBase(UserBase):
    id: UUID
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password: str


class Token(BaseModel):
    access_token: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: str | None = None

    class Config:
        orm_mode = True


class Ping(BaseModel):
    db: float
