from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TgBotSettings(BaseSettings):
    """
    Telegram Bot Settings
    """
    BOT_TOKEN: str
    ADMIN_ID: int
    GROUP_ID: int


class LoggingSettings(BaseSettings):
    """
    Logging Settings
    """
    LEVEL: int
    FORMAT: str


class Settings(TgBotSettings, LoggingSettings, BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


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
