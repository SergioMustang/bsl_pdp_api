from fastapi import status


class ApiException(Exception):
    status_code = None
    code = None
    message = None

    def __init__(self, status_code: int = None, code: str = None, message: str = None):
        self.status_code = status_code or self.__class__.status_code
        self.code = code or self.__class__.code
        self.message = message or self.__class__.message


class UserNotFoundException(ApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'user_does_not_exists'
    message = 'Пользователь не существует'


class CreateUserLoginConflictException(ApiException):
    status_code = status.HTTP_409_CONFLICT
    code = 'user_with_provided_login_exists'
    message = 'Пользователь с указанным логином уже существует'


class CreateUserEmailConflictException(ApiException):
    status_code = status.HTTP_409_CONFLICT
    code = 'user_with_provided_email_exists'
    message = 'Пользователь с таким адресом электронной почты существует'


class IncorrectAuthDataException(ApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'incorrect_login_or_password'
    message = 'Неверный логин или пароль'


class UserInactiveException(ApiException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = 'user_inactive'
    message = 'Ваш аккаунт отключен'


class CredentialException(ApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = 'wrong_credentials'
    message = 'Неверные данные для входа'


class SessionExpiredException(ApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = 'session_expired'
    message = 'Сессия закончилась. Введите ваши учетные данные снова'


class NotEnoughRights(ApiException):
    status_code = status.HTTP_403_FORBIDDEN
    code = 'not_enough_right_for_operation '
    message = 'Недостаточно прав для выполнения данной операции'


class UserNotFound(ApiException):
    status_code = status.HTTP_404_NOT_FOUND
    code = 'user_not_found '
    message = 'Пользователь не найден'
