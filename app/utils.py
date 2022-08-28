import datetime as dt
import typing as tp

import jwt
import pytz
from fastapi import (
    Depends,
)
from passlib.apps import custom_app_context as pwd_context
from fastapi.security import OAuth2PasswordBearer
from app.permissions import Permissions
from db import get_db, get_redis_connection
from db.models.user import (
    User,
)
from fastapi_pagination import Params
from fastapi_pagination.bases import (
    AbstractParams,
    BasePage,
    RawParams,
    T,
)
from pydantic import Field
from pydantic.types import conint
from jwt import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.settings import settings
from app.crud.user_crud import UserCRUD
from app.schemas.user import UserOutputSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/pdp/auth/v1/login')


def verify_text(
    text: str,
    hashed_text: str,
) -> bool:
    return pwd_context.verify(text, hashed_text)


def hash_text(text: str) -> str:
    return pwd_context.encrypt(text)


def check_user_is_active(user):
    if not user.is_active:
        raise exceptions.UserInactiveException


def auth_user(
    login: str,
    password: str,
    db: AsyncSession,
) -> tp.Optional[User]:
    user = UserCRUD(db=db, model=User).get_user_by_login(login=login)
    if not user or not verify_text(password, user.password):
        raise exceptions.IncorrectAuthDataException
    check_user_is_active(user)
    return user


def create_token_pair(user_id: int):
    access_token_data = {
        'token_type': 'access',
        'user_id': user_id,
        'exp': dt.datetime.now(
            tz=pytz.timezone(settings.TIME_ZONE)
        ) + dt.timedelta(
            minutes=settings.JWT_ACCESS_EXPIRE_MINUTES,
        ),
    }
    refresh_token_data = {
        'token_type': 'refresh',
        'user_id': user_id,
        'exp': dt.datetime.now(
            tz=pytz.timezone(settings.TIME_ZONE)
        ) + dt.timedelta(
            minutes=settings.JWT_REFRESH_EXPIRE_MINUTES,
        ),
    }
    return jwt.encode(access_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM), \
        jwt.encode(refresh_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    check_blacklist_token(token)
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_aud': False},
        )
        user_id: int = payload.get('user_id')

    except ExpiredSignatureError:
        raise exceptions.SessionExpiredException
    except Exception:
        raise exceptions.CredentialException

    user_obj = db.execute(select(User).filter(User.id == user_id)).scalar()
    if user_obj is None:
        raise exceptions.CredentialException
    check_user_is_active(user_obj)
    return UserOutputSchema.from_orm(user_obj)


def get_current_user_manual(
    token: str,
    db: AsyncSession,
    by_refresh_token: bool = False,
):
    check_blacklist_token(token)
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_aud': False},
        )
        user_id: int = payload.get('user_id')

        try:
            token_type: str = payload.get('token_type')
        except AttributeError:  # обнуляет старые токены (у которых не указан тип)
            raise exceptions.SessionExpiredException

    except ExpiredSignatureError:
        raise exceptions.SessionExpiredException
    except Exception:
        raise exceptions.CredentialException

    if token_type != ('refresh' if by_refresh_token else 'access'):
        raise exceptions.CredentialException

    user_obj = db.execute(select(User).filter(User.id == user_id)).scalar()
    if user_obj is None:
        raise exceptions.CredentialException
    check_user_is_active(user_obj)
    return UserOutputSchema.from_orm(user_obj)


def check_blacklist_token(token):
    r = get_redis_connection()
    blacklist_token = r.get(token)
    if blacklist_token is not None:
        raise exceptions.SessionExpiredException


def ban_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_aud': False},
        )
        expiration_date: int = payload.get('exp')
    except ExpiredSignatureError:
        pass
    r = get_redis_connection()
    try:
        check_blacklist_token(str(token))
    except exceptions.SessionExpiredException:
        pass
    r.set(str(token), expiration_date)


class PermissionValidator:
    def __init__(self, permissions: tp.Optional[list[Permissions]]):
        self.permissions = permissions

    def __call__(self, user: UserOutputSchema = Depends(get_current_user)):
        user_permission_names = [user_permission.name for user_permission in user.role.permissions]
        for permission in self.permissions:
            if permission not in user_permission_names:
                raise exceptions.NotEnoughRights
        return user


class ModifiedParams(Params):
    page: tp.Optional[int] = Field(1, ge=1, description="Page number")
    size: tp.Optional[int] = Field(50, ge=1, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class Paginate(BasePage[T], tp.Generic[T]):
    page: conint(ge=1)  # type: ignore
    size: conint(ge=1)  # type: ignore

    __params_type__ = ModifiedParams

    @classmethod
    def create(
        cls,
        items: tp.Sequence[T],
        total: int,
        params: AbstractParams,
    ):
        if not isinstance(params, ModifiedParams):
            raise ValueError("Page should be used with Params")

        return cls(
            total=total,
            items=items,
            page=params.page,
            size=params.size,
        )

