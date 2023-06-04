from dependency_injector import containers, providers

from src.domain.jwt_token.use_cases.add_jwt_tokens_to_blacklist import AddJwtTokensToBlacklist
from src.domain.jwt_token.use_cases.create_jwt_tokens import CreateJwtTokens
from src.domain.jwt_token.use_cases.decode_jwt_token import DecodeJwtToken
from src.domain.user.admin_use_cases.change_password import ChangePasswordAdmin
from src.domain.user.use_cases.authenticate import Authenticate
from src.domain.user.use_cases.register import Register
from src.domain.user.use_cases.retrieve_user import RetrieveUser


class UseCases(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    config = providers.Configuration()

    register = providers.Factory(Register, uow=repositories.uow)
    authenticate = providers.Factory(Authenticate, uow=repositories.uow)
    create_jwt_tokens = providers.Factory(CreateJwtTokens, uow=repositories.uow, config=config.app)
    decode_jwt_token = providers.Factory(DecodeJwtToken, uow=repositories.uow, config=config.app)
    add_jwt_tokens_to_blacklist = providers.Factory(AddJwtTokensToBlacklist, uow=repositories.uow)
    retrieve_user = providers.Factory(RetrieveUser, uow=repositories.uow)

    # Admin extra action use cases
    change_password_admin = providers.Factory(ChangePasswordAdmin, uow=repositories.uow)