from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.redis.dev', env_file_encoding='utf-8')
    redis_host: str
    redis_port: int
    redis_db: int


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.db.dev', env_file_encoding='utf-8')
    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: int
    db_name: str


class TgBotSettings(BaseSettings):

    bot_token: str
    admin_id: int
    chat_id: int
    admin_tel: str


class Logging(BaseSettings):
    format: str
    debug: bool


class Webhooks(BaseSettings):
    host: str
    path: str
    webapp_host: str
    webapp_port: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict()
    tgbot: TgBotSettings = TgBotSettings()
    redis: RedisSettings = RedisSettings()
    postgres: PostgresSettings = PostgresSettings()
    webhooks: Optional[Webhooks] = None

    # @property
    # def db_url(self):
    #     return URL.create(
    #         drivername=f"postgresql+asyncpg",
    #         username=self.postgres.pg_user,
    #         password=self.postgres.pg_password,
    #         host=self.postgres.pg_host,
    #         port=self.postgres.pg_port,
    #         database=self.postgres.db_name
    #         ).render_as_string()


