from typing import Callable, Sequence

from sqlalchemy.exc import IntegrityError

from src.common.exceptions.handlers.exception_parsers import (
    parse_unique_violation_error,
    parse_foreign_key_violation_error,
    ExceptionParserResult,
)

DEFAULT_EXCEPTION_PARSERS = (parse_unique_violation_error, parse_foreign_key_violation_error)


def handle_integrity_exception(
    exc: IntegrityError,
    parsers: Sequence[Callable[[IntegrityError], ExceptionParserResult | None]] | None = None,
) -> ExceptionParserResult:
    if not isinstance(exc, IntegrityError):
        raise exc

    if parsers is None:
        parsers = DEFAULT_EXCEPTION_PARSERS

    for parser in parsers:
        result = parser(exc)
        if result is None:
            continue
        return result
    else:
        raise exc
