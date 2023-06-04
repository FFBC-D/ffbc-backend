from enum import Enum


class ErrorCode(str, Enum):
    AUTH_ERROR = "auth_error"
    NOT_FOUND = "not_found"
    UNIQUE_ERROR = "unique_error"
    FOREIGN_KEY_ERROR = "foreign_key_error"
