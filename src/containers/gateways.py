from dependency_injector import containers, providers

from src.common.database.db import get_db_session


class Gateways(containers.DeclarativeContainer):
    config = providers.Configuration()
    db = providers.Singleton(get_db_session, config=config.database)
