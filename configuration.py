from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int


class PostgresSettings(BaseSettings):
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    DB_NAME: str


class TgBotSettings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    CHAT_ID: int
    ADMIN_TEL: str


# class Logging(BaseSettings):
#     format: str = Field(env='')
#     debug: bool = Field(env='')
#
#
# class Webhooks(BaseSettings):
#     host: str = Field(env='')
#     path: str = Field(env='')
#     webapp_host: str = Field(env='')
#     webapp_port: int = Field(env='')


class Settings(TgBotSettings, PostgresSettings, RedisSettings, BaseSettings):
    model_config = SettingsConfigDict(env_file='.dev.env', env_file_encoding='utf-8')
    TESTING: bool

    @property
    def db_url(self):
        return URL.create(
            drivername=f"postgresql+asyncpg",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            database=self.DB_NAME
        ).render_as_string(hide_password=False)


@lru_cache()
def get_settings():
    return Settings()


# Get data from .env
settings = get_settings()
