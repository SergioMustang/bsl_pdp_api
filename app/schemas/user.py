import datetime as dt
import enum
import re
from typing import Optional, Union

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    validator,
)


class TokenSchema(BaseModel):
    access_token: str = Field(..., title='JWT access-токен')
    refresh_token: str = Field(..., title='JWT refresh-токен')
    token_type: str = Field('bearer', title='Тип токенов')


class PermissionSchema(BaseModel):
    id: int = Field(..., title='Индентификатор')
    name: str = Field(..., title='Название')
    title: str = Field(..., title='Исходное название')

    class Config:
        orm_mode = True


class RoleSchema(BaseModel):
    id: int = Field(..., title='Индентификатор')
    name: str = Field(..., title='Название')
    title: str = Field(..., title='Исходное название')
    permissions: Optional[list[PermissionSchema]] = Field([], title='Индентификатор')

    class Config:
        orm_mode = True


class UserBaseSchema(BaseModel):
    login: str = Field(..., title='Логин')
    full_name: str = Field(..., title='ФИО')
    email: Optional[EmailStr] = Field(..., title='Почта')
    is_active: bool = Field(..., title='Активен', description='Активен ли пользователь')
    phone_number: Optional[str] = Field(None, title='Телефонный номер')
    city: Optional[str] = Field(None, title='Город')
    address: Optional[str] = Field(None, title='Адрес')
    zip_code: Optional[str] = Field(None, title='Почтовый индекс')

    class Config:
        orm_mode = True


class UserOutputSchema(UserBaseSchema):
    id: int = Field(..., title='Индентификатор')
    role: Optional[RoleSchema]
    created_at: dt.datetime = Field(..., title='Дата добавления')

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = Field(None, title='ФИО')
    email: Optional[EmailStr] = Field(None, title='Почта')
    is_active: Optional[bool] = Field(None, title='Активен')
    phone_number: Optional[str] = Field(None, title='Телефонный номер')
    city: Optional[str] = Field(None, title='Город')
    address: Optional[str] = Field(None, title='Адрес')
    zip_code: Optional[str] = Field(None, title='Почтовый индекс')

    class Config:
        orm_mode = True


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., title='Пароль', description='Пароль')
    role_id: int = Field(..., title='Индентификатор роли')

    @validator('login')
    def validate_login(cls, v):
        if len(v) < 5 or len(v) > 255:
            raise ValueError('Недопустимый размер имени пользователя')
        if re.match("^[a-zA-Zа-яА-Я0-9-_@]*$", v) is None:
            raise ValueError('В имени пользователя присутвуют недопустмые символы')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 5 or len(v) > 20:
            raise ValueError('Недопустимый размер строки')
        if re.match("^[a-zA-Z0-9-_.]*$", v) is None:
            raise ValueError('В пароле присутвуют недопустмые символы')
        return v


class UserFiltersSchema(BaseModel):
    full_name: Optional[str] = Field(None, title='ФИО')
    email: Optional[EmailStr] = Field(None, title='Почта')
    is_active: Optional[bool] = Field(None, title='Активен')
    phone_number: Optional[str] = Field(None, title='Телефонный номер')
    city: Optional[str] = Field(None, title='Город')
    address: Optional[str] = Field(None, title='Адрес')
    zip_code: Optional[str] = Field(None, title='Почтовый индекс')
    role_title: Optional[str] = Field(None, title='Роль')
    id: Optional[list[int]] = Field(None, title='Список Id пользователей')


class UserOrderingAsc(str, enum.Enum):
    id = 'id'
    created_at = 'created_at'
    full_name = 'full_name'
    email = 'email'
    city = 'city'
    zip_code = 'zip_code'


class UserOrderingDesc(str, enum.Enum):
    id = 'id desc'
    created_at = 'created_at desc'
    full_name = 'full_name desc'
    email = 'email desc'
    city = 'city desc'
    zip_code = 'zip_code desc'


class UserOrderingRoleAsc(str, enum.Enum):
    title = 'role_title'


class UserOrderingRoleDesc(str, enum.Enum):
    title = 'role_title desc'


class UserOrderingSchema(BaseModel):
    ordering: Union[
        UserOrderingAsc,
        UserOrderingDesc,
        UserOrderingRoleAsc,
        UserOrderingRoleDesc,
        None,
    ] = Field(None, title='Сортировка')

