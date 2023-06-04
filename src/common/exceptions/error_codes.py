from enum import Enum


class ErrorCode(str, Enum):
    NOT_FOUND = "not_found"
    UNIQUE_ERROR = "unique_error"
    FOREIGN_KEY_ERROR = "foreign_key_error"
