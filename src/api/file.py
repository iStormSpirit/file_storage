import pickle
from logging import config, getLogger

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from db.db import get_session, redis
from schemas import file as file_schema
from schemas import user as user_schema
from services.auth import get_current_user
from services.base import file_crud

config.dictConfig(LOGGING)
logger = getLogger(__name__)
router = APIRouter()


@router.get('/search', tags=['file'], response_model=list[file_schema.File])
async def search_files(*, db: AsyncSession = Depends(get_session),
                       current_user: user_schema.User = Depends(get_current_user),
                       extension: str = None, file_name: str = None,
                       limit: int = 100) -> list[File]:
    user = current_user
    result = await file_crud.search_files(db=db, user=user, extension=extension, file_name=file_name, limit=limit)
    logger.info(f'user: {user.id} requested file with query: {extension} - {file_name} - {limit}')
    return result


@router.get('/files/list', tags=['file'])
async def get_files_list(db: AsyncSession = Depends(get_session),
                         current_user: user_schema.User = Depends(get_current_user)):
    cache = await redis.get(str(current_user.id))
    if cache is None:
        files = await file_crud.get(db=db, user=current_user)
        await redis.set(str(current_user.id), pickle.dumps(files), ex=60)
    cache = pickle.loads(await redis.get(str(current_user.id)))
    data = {'account_id': current_user.id, 'files': cache}
    return data


@router.get('/download', tags=['file'])
async def download_file(*, db: AsyncSession = Depends(get_session),
                        current_user: user_schema.User = Depends(get_current_user),
                        identifier: str | int = None,
                        download_folder: bool = False,
                        ) -> File:
    if download_folder:
        file = await file_crud.download_folder(user=current_user, path=identifier)
        logger.info(f'user: {current_user.id} download folders by path: {identifier} ')
    else:
        file = await file_crud.download_file(db=db, user=current_user, identifier=identifier)
        logger.info(f'user: {current_user.id} download file by path: {identifier} ')
    return file


@router.post('/upload', tags=['file'], response_model=file_schema.File)
async def upload_file(*, file: UploadFile = File(...),
                      path: str = None, file_name: str = None,
                      current_user: user_schema.User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_session)) -> File:
    file_upload = await file_crud.create(db=db, user=current_user, path=path, name=file_name, file=file)
    logger.info(f'user: {current_user.id} upload file: {file_name} - path: {path} ')
    return file_upload
