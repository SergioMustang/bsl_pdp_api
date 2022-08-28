from typing import Optional

from db.models.user import User
from sqlalchemy import (
    select,
)
from app.crud.base import CRUDBase
from app.schemas.user import (
    UserFiltersSchema,
    UserOrderingSchema,
    UserOrderingAsc,
    UserOrderingDesc,
    UserOrderingRoleAsc,
    UserOrderingRoleDesc,
)
from sqlalchemy import (
    String,
    cast,
    or_,
    select,
)
from db.models.user import Role


class UserCRUD(CRUDBase):

    def get_user_by_login(
        self,
        login: str,
    ) -> Optional[User]:
        query = self.db.execute(select(User).filter(User.login == login))
        self.db.commit()
        user = query.scalars().first()
        return user

    def get_user_by_id(
        self,
        user_id: int,
    ) -> Optional[User]:
        query = self.db.execute(select(User).filter(User.id == user_id))
        self.db.commit()
        user = query.scalars().first()
        return user

    def get_users(
        self,
        search: Optional[str] = None,
        filters: Optional[UserFiltersSchema] = None,
        ordering: Optional[UserOrderingSchema] = None,
    ):
        query = select(self.model)
        # Только активные пользователи
        query = query.filter(self.model.is_active == True)
        if search:
            query = query.filter(
                or_(
                    cast(self.model.id, String).ilike(f'%{search}%'),
                    self.model.full_name.ilike(f'%{search}%'),
                    self.model.email.ilike(f'%{search}%'),
                    self.model.phone_number.ilike(f'%{search}%'),
                    self.model.city.ilike(f'%{search}%'),
                    self.model.address.ilike(f'%{search}%'),
                    self.model.zip_code.ilike(f'%{search}%'),
                    self.model.role.has(Role.title.ilike(f'%{search}%')),
                )
            )
        if filters:
            for key, value in filters:
                if key not in filters.__fields_set__:
                    continue
                else:
                    if key == 'role_title':
                        query = query.filter(self.model.role.has(Role.title.ilike(f'%{value}%')))
                    elif type(value) == str:
                        query = query.filter(getattr(self.model, key).ilike(f'%{value}%'))
                    elif type(value) == list:
                        query = query.filter(getattr(self.model, key).in_(value))

        if ordering:
            ordering_param = ordering.ordering
            if ordering_param in UserOrderingAsc:
                query = query.order_by(getattr(self.model, ordering_param.name).asc())
            elif ordering_param in UserOrderingDesc:
                query = query.order_by(getattr(self.model, ordering_param.name).desc())
            elif ordering_param in UserOrderingRoleAsc:
                query = (
                    query.join(self.model.role)
                    .order_by(getattr(Role, ordering_param.name).asc())
                )
            elif ordering_param in UserOrderingRoleDesc:
                query = (
                    query.join(self.model.role)
                    .order_by(getattr(Role, ordering_param.name).desc())
                )
        else:
            query = query.order_by(self.model.created_at.desc())

        users = self.db.execute(query).scalars().all()

        return users
