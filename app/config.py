import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV_FILENAME = os.environ.get("DOTENV", ".env")


class AppSettings(BaseSettings):

    LOGGING_CONFIG_FILE: str
    APP_SYS_NAME: str

    TIMEZONE: str
    DISCORD_TOKEN: str
    SUMMARY_POST_AT_LOCALTIME: str
    DISCORD_POST_MESSAGE_CHANNEL: int
    RENDER_TEMPLATE_FILE: str

def get_config() -> AppSettings:
    """
    Get the configuration settings based on the current config environment.
    """

    if not Path(ENV_FILENAME).exists():
        raise RuntimeError(f"Config file '{ENV_FILENAME}' does not exist.")

    load_dotenv(dotenv_path=ENV_FILENAME, override=True)

    return AppSettings()  # type: ignore


