from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    Body
)
from fastapi.security import OAuth2PasswordRequestForm
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app import (
    schemas,
    utils,
)
from app.core import exceptions
from app.core.settings import settings
from app.schemas.user import UserOutputSchema, TokenSchema


auth_router = APIRouter(
    prefix=f'/api/{settings.PROJECT_URL_PREFIX}/auth/v1',
    tags=['auth'],
)


@auth_router.post(
    '/login',
    summary='Вход пользователя',
    response_model=TokenSchema,
)
def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = utils.auth_user(login=login_data.username, password=login_data.password, db=db)
    access_token, refresh_token = utils.create_token_pair(user_id=user.id)
    return schemas.user.TokenSchema(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    '/refresh',
    summary='Получение новой пары токенов',
    response_model=TokenSchema,
)
def refresh(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    user = utils.get_current_user_manual(token=refresh_token, db=db, by_refresh_token=True)
    utils.check_user_is_active(user)
    utils.ban_token(refresh_token)

    access_token, refresh_token = utils.create_token_pair(user_id=user.id)
    return schemas.user.TokenSchema(access_token=access_token, refresh_token=refresh_token)


@auth_router.get(
    '/current_user',
    summary='Получение информации о текущем пользователе',
    response_model=UserOutputSchema,
)
def current_user(
    user=Depends(utils.get_current_user),
):
    if user is None:
        raise exceptions.UserNotFoundException
    return user


@auth_router.get(
    '/logout',
    summary='Выход пользователя из системы',
    status_code=204,
)
def logout(
    user=Depends(utils.get_current_user),
    token=Depends(utils.ban_token),
    db: AsyncSession = Depends(get_db),
):
    return Response(status_code=status.HTTP_204_NO_CONTENT)
