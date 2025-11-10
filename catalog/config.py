import os
from pathlib import Path

import msgspec


class SecretConfig(msgspec.Struct):
    allowed_hosts: list[str]
    config_secret_key: str
    log_level: str
    pepper: str


class StaticConfig(msgspec.Struct):
    static_url: str
    static_root: str
    media_url: str
    media_root: str


class PostgresConfig(msgspec.Struct):
    host: str
    port: int
    login: str
    password: str
    database: str


class RedisConfig(msgspec.Struct):
    host: str
    port: int
    db: int
    password: str


class Config(msgspec.Struct):
    secret: SecretConfig
    static: StaticConfig
    postgres: PostgresConfig
    redis: RedisConfig

    @classmethod
    def load(cls) -> "Config":
        base_dir = Path(__file__).resolve().parent

        def _split_hosts(value: str) -> list[str]:
            return [] if not value else value.split(",")

        return cls(
            secret=SecretConfig(
                allowed_hosts=_split_hosts(os.getenv("APP_ALLOWED_HOSTS", "")),
                config_secret_key=os.getenv("APP_CONFIG_ENCRYPTION_KEY", ""),
                log_level=os.getenv("APP_LOG_LEVEL", "info"),
                pepper=os.getenv("APP_PEPPER", ""),
            ),
            static=StaticConfig(
                static_url=os.getenv("STATIC_URL", "/static/"),
                static_root=str(base_dir / os.getenv("STATIC_ROOT", "staticfiles")),
                media_url=os.getenv("MEDIA_URL", "/media/"),
                media_root=str(base_dir / os.getenv("MEDIA_ROOT", "media")),
            ),
            postgres=PostgresConfig(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                login=os.getenv("POSTGRES_USER", "user"),
                password=os.getenv("POSTGRES_PASSWORD", "pass"),
                database=os.getenv("POSTGRES_DB", "catalog"),
            ),
            redis=RedisConfig(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_SESSIONS_DB", "0")),
                password=os.getenv("REDIS_PASSWORD", ""),
            ),
        )
