from dependency_injector import containers, providers

from src.config.settings import Settings
from src.containers.gateways import Gateways
from src.containers.repositories import Repositories
from src.containers.use_cases import UseCases
from src.data.database.models import start_mappers

start_mappers()


class Container(containers.DeclarativeContainer):
    config: Settings = providers.Configuration(pydantic_settings=[Settings()])
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.api",
            "src.common.dependencies",
        ]
    )
    gateways = providers.Container(Gateways, config=config)
    repositories = providers.Container(Repositories, gateways=gateways)
    use_cases = providers.Container(UseCases, repositories=repositories, config=config)


container = Container()
