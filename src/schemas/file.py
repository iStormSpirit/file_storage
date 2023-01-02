from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ORM(BaseModel):
    class Config:
        orm_mode = True


class FileCreate(ORM):
    name: str


class FileBase(ORM):
    id: UUID
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool


class File(FileBase):
    pass
