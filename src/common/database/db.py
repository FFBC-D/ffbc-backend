from asyncio import current_task

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker


def get_db_session(config: dict):
    async_engine = create_async_engine(config["dsn"], echo=False, future=True)
    return async_scoped_session(
        sessionmaker(  # type: ignore
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        ),
        scopefunc=current_task,
    )
