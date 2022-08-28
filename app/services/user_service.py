from app.core import exceptions
import app.utils as utils
from app.crud.user_crud import UserCRUD
from db.models.user import User
from app.schemas.user import UserUpdateSchema
from app.core.exceptions import UserNotFound


class UserService:
    """ Service class for work with SupplierRequest """

    def __init__(self, db):
        self.crud = UserCRUD(db=db, model=User)

    def create_user(self, user_create):
        if self.crud.get_user_by_login(login=user_create.login):
            raise exceptions.CreateUserLoginConflictException

        user = User(
            login=user_create.login,
            email=user_create.email,
            password=utils.hash_text(user_create.password),
            full_name=user_create.full_name,
            city=user_create.city,
            address=user_create.address,
            zip_code=user_create.zip_code,
            role_id=user_create.role_id,
            is_active=True,
        )

        return self.crud.create(user)

    def deactivate_user(self, user_id):
        user = self.crud.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        if user.is_active is False:
            pass
        else:
            new_data = UserUpdateSchema()
            new_data.is_active = False
            self.crud.update(user, new_data)

    def update_user(self, user_id, data_for_update):
        user = self.crud.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        if (data_for_update.is_active in [None, False]) and user.is_active is False:
            raise UserNotFound
        return self.crud.update(user, data_for_update)

    def get_user(self, user_id):
        user = self.crud.get_user_by_id(user_id)
        if user is None or user.is_active is False:
            raise UserNotFound
        return user

    def get_users(self, search, filters, ordering):
        return self.crud.get_users(
            search=search,
            filters=filters,
            ordering=ordering
        )
