from dataclasses import dataclass


@dataclass
class UserAdminFilterQuery:
    id: int | None = None
    email: str | None = None
    phone: str | None = None
