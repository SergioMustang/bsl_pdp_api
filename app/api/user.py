from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    Body
)
from typing import Optional
from fastapi_pagination import paginate
from db import get_db
from app.schemas.user import (
    UserOutputSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserFiltersSchema,
    UserOrderingSchema
)
from sqlalchemy.orm import Session
from app.utils import (
    get_current_user,
    Paginate,
    ModifiedParams,
    PermissionValidator
)
from app.core.settings import settings
from app.services.user_service import UserService
from app.permissions import Permissions
from mq import NatsQuery

user_router = APIRouter(
    prefix=f'/api/{settings.PROJECT_URL_PREFIX}/user/v1',
    tags=['user'],
)


@user_router.post(
    '/user',
    summary='Добавление пользователя',
    response_model=UserOutputSchema,
)
async def add_user(
        user_create: UserCreateSchema,
        user=Depends(PermissionValidator([Permissions.USER_MANAGEMENT])),
        db: Session = Depends(get_db),
):
    user_obj = UserService(db).create_user(user_create)
    user_scheme_obj = UserOutputSchema.from_orm(user_obj)
    try:
        async with NatsQuery() as nc:
            await nc.send_json_message(subject='reg', json_obj=user_scheme_obj)
    except Exception as e:
        pass
    return user_obj


@user_router.delete(
    '/user',
    summary='Деактивировать пользователя',
)
def deactivate_user(
        user_id: int,
        user=Depends(PermissionValidator([Permissions.USER_MANAGEMENT])),
        db: Session = Depends(get_db),
):
    UserService(db).deactivate_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch(
    '/user',
    summary='Обновить данные пользователя',
    response_model=UserOutputSchema
)
def update_user(
        user_id: int,
        data_for_update: UserUpdateSchema,
        user=Depends(PermissionValidator([Permissions.USER_MANAGEMENT])),
        db: Session = Depends(get_db),
):
    return UserService(db).update_user(user_id, data_for_update)


@user_router.get(
    '/user/{user_id}',
    summary='Получить пользователя по id',
    response_model=UserOutputSchema
)
def get_user(
        user_id: int,
        user=Depends(PermissionValidator([Permissions.USER_MANAGEMENT])),
        db: Session = Depends(get_db),
):
    return UserService(db).get_user(user_id)


@user_router.post(
    '/users',
    summary='Получение списка пользователей',
    response_model=Paginate[UserOutputSchema],
)
def get_users(
        params: ModifiedParams,
        user=Depends(get_current_user),
        search: Optional[str] = Body(None),
        filters: Optional[UserFiltersSchema] = Body(None),
        ordering: Optional[UserOrderingSchema] = Body(None),
        db: Session = Depends(get_db),

):
    return paginate(
        sequence=UserService(db).get_users(search, filters, ordering),
        params=params,
    )
