from sqlalchemy.orm import registry


def start_mappers() -> None:
    from src.data.database.models.user import User  # noqa: F401
    from src.data.database.models.jwt import OutstandingToken, BlacklistToken  # noqa: F401


mapper_registry = registry()
