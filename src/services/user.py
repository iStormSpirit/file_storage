import pathlib
import shutil
import time
from typing import Any, Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import Base

from .auth import get_password_hash, verify_password

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id) -> ModelType | None:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip=0, limit=100) -> list[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        hash_password = get_password_hash(obj_in.dict().pop('password'))
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['password'] = hash_password
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in) -> ModelType:
        pass

    async def delete(self, db: AsyncSession, *, user) -> ModelType | None:
        db_obj = await self.get(db=db, id=user.id)
        path = f'{pathlib.Path.cwd()}/{user.username}'
        shutil.rmtree(path)
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def get_status(self, db: AsyncSession) -> Any:
        start_time = time.time()
        statement = select(self._model)
        await db.execute(statement=statement)
        ping = time.time() - start_time
        return {
            'db': '{:.4f}'.format(ping),
        }
