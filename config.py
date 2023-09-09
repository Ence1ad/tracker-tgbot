from functools import lru_cache

from apscheduler.jobstores.redis import RedisJobStore
from pydantic import Field
from aiogram.fsm.storage import redis
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import ConnectionPool
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
    DB_USER: str
    DB_USER_PASS: str


class TgBotSettings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    CHAT_ID: int
    ADMIN_TEL: str


class ProjectSettings(BaseSettings):
    LENGTH_NAME_LIMIT: int = Field(default=10)
    USER_ACTIONS_LIMIT: int = Field(default=2)
    USER_CATEGORIES_LIMIT: int = Field(default=2)
    USER_WEEK_TRACKERS_LIMIT: int = Field(default=100)
    MAX_HOURS_DURATION_TRACKER: int = Field(default=23)


class LoggingSettings(BaseSettings):
    LEVEL: int
    FORMAT: str

# class Webhooks(BaseSettings):
#     host: str = Field(env='')
#     path: str = Field(env='')
#     webapp_host: str = Field(env='')
#     webapp_port: int = Field(env='')


class Settings(TgBotSettings, LoggingSettings, PostgresSettings, RedisSettings, ProjectSettings, BaseSettings):
    # model_config = SettingsConfigDict(env_file='dev.env', env_file_encoding='utf-8')
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    TESTING: bool

    @property
    def db_url(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_USER_PASS,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB
        ).render_as_string(hide_password=False)

    # @property
    # def cache_url(self):
    #     return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def create_redis_pool(self, max_connections: int = 10) -> ConnectionPool:
        pool: ConnectionPool = redis.ConnectionPool(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            db=self.REDIS_DB,
            password=self.REDIS_PASSWORD,
            max_connections=max_connections
        )
        return pool

    @property
    def scheduler_job_stores(self) -> dict[str, RedisJobStore]:
        scheduler_job_stores = {
            'default': RedisJobStore(
                jobs_key='dispatched_trips_jobs',
                run_times_key='dispatched_trips_running',
                host=self.REDIS_HOST,
                db=self.REDIS_DB,
                port=self.REDIS_PORT,
                password=self.REDIS_PASSWORD,
            )
        }
        return scheduler_job_stores


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Get data from .env
settings = get_settings()
