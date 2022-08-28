import enum


class Permissions(str, enum.Enum):
    USER_MANAGEMENT = 'user_management'

    def __str__(self) -> str:
        return self.value
