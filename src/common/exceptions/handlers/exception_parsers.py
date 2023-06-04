import re
from typing import NamedTuple

from sqlalchemy.exc import IntegrityError

from src.common.exceptions.error_codes import ErrorCode


class ExceptionParserResult(NamedTuple):
    message: str
    error_code: ErrorCode
    field: str


def parse_unique_violation_error(exc: IntegrityError) -> ExceptionParserResult | None:
    pattern = re.compile(r"DETAIL\:\s+Key \((?P<field>.+?)\)=\((?P<value>.+?)\) already exists")
    match = pattern.search(str(exc))
    default_message = "This value already exists"
    return (
        ExceptionParserResult(
            field=match["field"],
            error_code=ErrorCode.UNIQUE_ERROR,
            message=default_message,
        )
        if match is not None
        else None
    )


def parse_foreign_key_violation_error(exc: IntegrityError) -> ExceptionParserResult | None:
    pattern = re.compile(
        r"DETAIL\:\s+Key \((?P<field>.+?)\)=\((?P<value>.+?)\) is not present in (?P<table>.+?)"
    )
    match = pattern.search(str(exc))
    default_message = "Foreign key doesn't exists"
    return (
        ExceptionParserResult(
            field=match["field"],
            error_code=ErrorCode.FOREIGN_KEY_ERROR,
            message=default_message,
        )
        if match is not None
        else None
    )
