from sqlalchemy import select

from src.common.filters import FilterSet, Filter
from src.common.repository import BaseRepo
from src.data.database.models.user import User
from src.domain.user.dto.filter import UserFilterSchema


class UserFilterSet(FilterSet):
    id = Filter(User, "id")
    email = Filter(User, "email")


class UserRepo(BaseRepo[User, UserFilterSchema]):
    model = User
    query = select(User)
    filter_set = UserFilterSet
