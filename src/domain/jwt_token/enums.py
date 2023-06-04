from enum import Enum


class JwtTokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
