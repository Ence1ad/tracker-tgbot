from functools import lru_cache

from apscheduler.jobstores.redis import RedisJobStore
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class LoggingSettings(BaseSettings):
    """Logging Settings."""

    LEVEL: int
    FORMAT: str


class PostgresSettings(BaseSettings):
    """PostgreSQL Settings."""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DB_USER: str
    DB_USER_PASS: str


class ProjectSettings(BaseSettings):
    """Project Settings."""

    THROTTLING_RATE_LIMIT: int = Field(default=10)  # Maximum number of messages
    THROTTLING_RATE_PERIOD: int = Field(default=10)  # Time period in seconds
    RU_LANG_CODE: str = Field(default='ru')
    EN_LANG_CODE: str = Field(default='en')
    GLOBAL_LANG_CODE: str = Field(default='en')
    USER_REPORT_DIR: str = Field(default='./reports/')


class RedisSettings(BaseSettings):
    """Redis Settings."""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str


class TgBotSettings(BaseSettings):
    """Telegram Bot Settings."""

    BOT_TOKEN: str
    ADMIN_ID: int
    GROUP_ID: int


class Settings(LoggingSettings, PostgresSettings, ProjectSettings, RedisSettings, TgBotSettings,  BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def cache_url(self) -> str:
        """
        The cache_url function returns a string that is the URL for connection to the Redis database.

        :param self: Access the class attributes
        :return: A string containing the connection url for a redis database
        """
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}?protocol=3"

    @property
    def db_url(self) -> str:
        """
        The db_url function returns a string that is the URL for connecting to the database.

        :param self: Reference the class itself
        :return: A string that is a connection url for the database
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_USER_PASS,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB
        ).render_as_string(hide_password=False)

    @property
    def scheduler_job_stores(self) -> dict[str, RedisJobStore]:
        """
        The scheduler_job_stores function is used to configure the job stores that are available to the scheduler.

        The function should return a dictionary of job store configurations, keyed by name.

        :param self: Represent the instance of the class
        :return: A dictionary with a single key-value pair
        """
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
    """
    Return an instance of the Settings class.

    The Settings class contains all the settings for this project,
    and it's used by other modules to access those settings.

    :return: A settings object
    """
    return Settings()


# Get data from .env
settings = get_settings()
