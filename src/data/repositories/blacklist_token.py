from sqlalchemy import select

from src.common.filters import FilterSet, Filter
from src.common.repository import BaseRepo
from src.data.database.models.jwt import BlacklistToken, OutstandingToken
from src.domain.jwt_token.dto.filter import BlacklistTokenFilterSchema


class BlacklistTokenFilterSet(FilterSet):
    outstanding_token_id = Filter(BlacklistToken, "outstanding_token_id")


class BlacklistTokenRepo(BaseRepo[BlacklistToken, BlacklistTokenFilterSchema]):
    model = BlacklistToken
    query = select(BlacklistToken).join(OutstandingToken)
    filter_set = BlacklistTokenFilterSet
