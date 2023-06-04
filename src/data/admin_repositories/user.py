from sqlalchemy import select

from src.common.filters import FilterSet, Filter, ILikeFilter
from src.common.repository import BaseRepo
from src.data.database.models.user import User
from src.domain.user.dto.admin import UserAdminFilterSchema


class UserAdminFilterSet(FilterSet):
    id = Filter(User, "id")
    email = ILikeFilter(User, "email")
    phone = ILikeFilter(User, "phone")


class UserAdminRepo(BaseRepo[User, UserAdminFilterSchema]):
    model = User
    query = select(User)
    filter_set = UserAdminFilterSet
