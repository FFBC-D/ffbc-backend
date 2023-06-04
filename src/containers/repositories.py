from dependency_injector import containers, providers

from src.data.uow import UnitOfWork


class Repositories(containers.DeclarativeContainer):
    gateways = providers.DependenciesContainer()
    uow = providers.Factory(UnitOfWork, scoped_session=gateways.db)
