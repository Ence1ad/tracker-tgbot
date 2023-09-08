from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str


class TgBotSettings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    CHAT_ID: int
    ADMIN_TEL: str


class LoggingSettings(BaseSettings):
    LEVEL: int
#     FORMAT: str
#
#
# class Webhooks(BaseSettings):
#     host: str = Field(env='')
#     path: str = Field(env='')
#     webapp_host: str = Field(env='')
#     webapp_port: int = Field(env='')


class Settings(TgBotSettings, LoggingSettings, PostgresSettings, RedisSettings,  BaseSettings):
    model_config = SettingsConfigDict(env_file='dev.env', env_file_encoding='utf-8')
    # model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    TESTING: bool

    @property
    def db_url(self):
        return URL.create(
            drivername=f"postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB
        ).render_as_string(hide_password=False)


@lru_cache()
def get_settings():
    return Settings()


# Get data from .env
settings = get_settings()
