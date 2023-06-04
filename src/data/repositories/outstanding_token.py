from sqlalchemy import select, Select

from src.common.filters import FilterSet, Filter, MethodFilter
from src.common.repository import BaseRepo
from src.data.database.models.jwt import OutstandingToken
from src.domain.jwt_token.dto.filter import OutstandingTokenFilterSchema


class OutstandingTokenFilterSet(FilterSet):
    jti = Filter(OutstandingToken, "jti")
    user_id = Filter(OutstandingToken, "user_id")
    in_blacklist = MethodFilter("filter_in_blacklist")

    def filter_in_blacklist(self, query: Select, value: bool) -> Select:
        if value is None:
            return query

        stmt = (
            OutstandingToken.blacklist_token != None
            if value
            else OutstandingToken.blacklist_token == None
        )
        return query.filter(stmt)


class OutstandingTokenRepo(BaseRepo[OutstandingToken, OutstandingTokenFilterSchema]):
    model = OutstandingToken
    query = select(OutstandingToken)
    filter_set = OutstandingTokenFilterSet
