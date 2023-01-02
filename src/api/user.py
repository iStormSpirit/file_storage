from logging import config, getLogger
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from db.db import get_session
from schemas import user as user_schema
from services import auth
from services.auth import get_current_user
from services.base import user_crud

config.dictConfig(LOGGING)
logger = getLogger(__name__)
router = APIRouter()


@router.post('/register', response_model=user_schema.User, status_code=status.HTTP_201_CREATED,
             tags=['user crud'])
async def create_user(*, db: AsyncSession = Depends(get_session), data: user_schema.UserCreate) -> Any:
    user = await user_crud.create(db=db, obj_in=data)
    logger.info(f'user: {data.username} is created')
    return user


@router.get('/user/{id}', response_model=user_schema.User, tags=['user crud'])
async def get_user_by_id(*, db: AsyncSession = Depends(get_session), id) -> Any:
    user = await user_crud.get(db=db, id=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='users by id not found')
    return user


@router.delete('/user/{id}/delete', tags=['user crud'])
async def delete_user(*, db: AsyncSession = Depends(get_session),
                      current_user: user_schema.User = Depends(get_current_user)) -> Any:
    user = await user_crud.delete(db=db, user=current_user)
    logger.info(f'user: {user.id} deleted')
    return user


@router.post('/token', response_model=user_schema.Token)
async def create_token(*, db: AsyncSession = Depends(get_session),
                       form_data: OAuth2PasswordRequestForm = Depends()):
    token = await auth.get_token(db=db, username=form_data.username, password=form_data.password)
    logger.info(f'user: {form_data.username} created token')
    return token


@router.get("/users/me/")
async def read_users_me(current_user: user_schema.User = Depends(get_current_user)):
    logger.info(f'user: {current_user.username} get self')
    return current_user


@router.get('/ping', response_model=user_schema.Ping, tags=['status'])
async def check_status_db(db: AsyncSession = Depends(get_session)) -> Any:
    result = await user_crud.get_status(db=db)
    logger.info(f'ping to db {result}')
    return result
