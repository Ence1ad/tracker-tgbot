from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    """
    Logging Settings
    """
    LEVEL: int
    FORMAT: str


class RedisSettings(BaseSettings):
    """
    Redis Settings
    """
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str


class TgBotSettings(BaseSettings):
    """
    Telegram Bot Settings
    """
    BOT_TOKEN: str
    ADMIN_ID: int
    GROUP_ID: int


class Settings(LoggingSettings, RedisSettings, TgBotSettings,  BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def cache_url(self) -> str:
        """
        The cache_url function returns a string that is the URL for connection to the Redis database.

        :param self: Access the class attributes
        :return: A string containing the connection url for a redis database
        """
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}?protocol=3"


@lru_cache
def get_settings() -> Settings:
    """
    Returns an instance of the Settings class.

    The Settings class contains all the settings for this project,
    and it's used by other modules to access those settings.

    :return: A settings object
    """
    return Settings()


# Get data from .env
settings = get_settings()
