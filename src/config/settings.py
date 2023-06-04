from typing import Optional, Any

from pydantic import BaseSettings, validator, PostgresDsn


class EnvBaseSettings(BaseSettings):
    class Config:
        env_file = ".env"


class AppSettings(EnvBaseSettings):
    debug: bool = True
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 60
    refresh_token_expires_minutes: int = 60

    class Config:
        env_prefix = "app_"


class PostgresSettings(EnvBaseSettings):
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: str = "5432"
    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    dsn: Optional[PostgresDsn] = None

    class Config:
        env_prefix = "postgres_"

    @validator("dsn", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.get("scheme"),
            user=values.get("user"),
            password=values.get("password"),
            host=values.get("host"),
            port=values.get("port"),
            path=f"/{values.get('db')}",
        )


class Settings(EnvBaseSettings):
    app: AppSettings = AppSettings()
    database: PostgresSettings = PostgresSettings()
