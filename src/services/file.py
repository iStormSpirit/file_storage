import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Generic, Type, TypeVar
from zipfile import ZIP_DEFLATED, ZipFile

import aiofiles
from fastapi import File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import Base
from models.models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, user: User):
        statement = (select(self._model).where(self._model.user_id == user.id))
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create_in_db(self, db: AsyncSession, user: User, path: str, name: str, size: int):
        db_obj = self._model(name=name, path=path, size=size, is_downloadable=True, user_id=user.id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def help_write_file(name: str, path: str, custom_name: str):
        file_format = name.split('.')[-1]
        end_file_name = name
        path_end = ''
        if path:
            path_end = path
        if custom_name:
            end_file_name = f'{custom_name}.{file_format}'
        full_path = f'{path_end}/{end_file_name}'
        return path_end, end_file_name, full_path

    async def create(self, db: AsyncSession, user: User, path: str, name: str, file: UploadFile = File()):
        path_end, file_name, full_path = await self.help_write_file(name=file.filename, path=path, custom_name=name)
        p = Path(f'{user.username}/{path_end}')
        p.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(f'{user.username}/{path_end}/{file_name}', 'wb') as out_file:
            while content := await file.read(1024):
                await out_file.write(content)
        file_size = os.path.getsize(f'{user.username}/{full_path}')
        result = await self.create_in_db(db=db, user=user, path=full_path, name=file_name, size=file_size)
        return result

    async def get_path_by_id(self, db, user, id):
        statement = select(self._model).where(self._model.id == id)
        file = await db.scalar(statement=statement)
        full_path = f'{user.username}/{file.path}'
        return full_path

    async def get_file_by_id(self, db, user: User, id: int) -> File:
        path = await self.get_path_by_id(db=db, id=id, user=user)
        return FileResponse(path=path)

    @staticmethod
    async def get_file_by_path(user: User, path: Path) -> File:
        full_path = f'{user.username}/{path}'
        response = FileResponse(path=full_path)
        return response

    async def download_file(self, db: AsyncSession, user: User, identifier: str | int):
        try:
            file = await self.get_file_by_id(db=db, user=user, id=int(identifier), )
        except ValueError:
            file = await self.get_file_by_path(user=user, path=Path(identifier), )
        except FileNotFoundError:
            return {'Exception': 'No such file'}
        return file

    async def search_files(self, db: AsyncSession, user: User, extension: str, file_name: str, limit: int):
        path = str(user.username)
        statement = (select(self._model).where(self._model.user_id == user.id))
        if file_name:
            statement = (statement.where(self._model.name.startswith(f'{file_name}')))
        elif extension:
            statement = (statement.where(self._model.name.endswith(f'.{extension}')))
        elif extension and file_name:
            statement = (
                statement.where(self._model.path == path).where(self._model.name.startswith(f'{file_name}')).where(
                    self._model.name.endswith(f'.{extension}')))
        else:
            return 'Please enter query parameters'
        statement = statement.limit(limit)
        result = await db.execute(statement=statement)
        return result.scalars().all()

    @staticmethod
    def zip_folder(file_list, name: str):
        zip_io = BytesIO()
        zip_name = datetime.now().strftime('%m-%d-%Y/%H:%M:%S')

        with ZipFile(zip_io, 'w', compression=ZIP_DEFLATED) as zip_file:
            for file in file_list:
                zip_file.write(file)
        response = StreamingResponse(iter([zip_io.getvalue()]), media_type='application/x-zip-compressed')
        response.headers['Content-Disposition'] = f'attachment; filename={name}_{zip_name}.zip'
        return response

    async def download_folder(self, user: User, path: str, ):
        full_path = f'{user.username}/{path}'
        name = path.split('/')[-1]
        file_list = [file for file in list(Path(full_path).iterdir())]
        archive = self.zip_folder(file_list, name=name)
        return archive
