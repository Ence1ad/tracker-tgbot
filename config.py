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
    RU_LANG_CODE: str = Field(default='ru')  # ISO 639-1 language code
    EN_LANG_CODE: str = Field(default='en')  # ISO 639-1 language code
    GLOBAL_LANG_CODE: str = Field(default='en')  # ISO 639-1 language code
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


class Settings(LoggingSettings, PostgresSettings, ProjectSettings, RedisSettings,
               TgBotSettings, BaseSettings):
    """Application settings class that combines various configuration settings.

    This class inherits from multiple configuration settings classes to create a
    composite configuration.

    Attributes
    ----------
        model_config (SettingsConfigDict): The model configuration settings.
            - env_file (str): The name of the environment file.
            - env_file_encoding (str): The encoding of the environment file.

    Properties:
        cache_url (str): A property that generates the Redis cache URL based on
        configuration settings.
        db_url (str): A property that generates the database URL based on configuration
        settings.
        scheduler_job_stores (dict[str, RedisJobStore]): A dictionary of job stores
        for the scheduler.
    """

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def cache_url(self) -> str:
        """Generate the Redis cache URL based on configuration settings.

        :return: str: The Redis cache URL.
        """
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/" \
               f"{self.REDIS_DB}?protocol=3"

    @property
    def db_url(self) -> str:
        """Generate the database URL based on configuration settings.

        :return: str: The database URL.
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
        """Get the dictionary of job stores for the scheduler.

        :return: dict[str, RedisJobStore]: A dictionary of job stores for the scheduler.
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
    """Get application settings.

    This function returns an instance of the `Settings` class, which represents the
    application's configuration settings. The settings include various configurations
    inherited from multiple configuration settings classes.

    :return: Settings: An instance of the `Settings` class containing application
     configuration settings.
    """
    return Settings()


# Get data from .env
settings = get_settings()
