import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV_FILENAME = os.environ.get("DOTENV", ".env")


class AppSettings(BaseSettings):

    LOGGING_CONFIG_FILE: str
    APP_SYS_NAME: str

    TIMEZONE: str
    DISCORD_TOKEN: str
    SUMMARY_POST_AT_LOCALTIME: str
    DISCORD_BOT_GUILD_ID: int
    DISCORD_BOT_CATEGORY_IDS: List[int]
    DISCORD_POST_MESSAGE_CHANNEL: int
    DISCORD_MAX_MESSAGE_LENGTH: int
    SUMMARY_USE_MULTIPLE_MESSAGES: bool
    RENDER_TEMPLATE_FILE: str
    RENDER_TIX_TEMPLATE_GRAPHIC_FILE: str
    RENDER_TIX_TEMPLATE_TEXT_FILE: str
    RENDER_TIX_REPLACE_WORD_FROM_NAME: str
    RENDER_CONTEXT: str
    HUMANITIX_API: str
    HUMANITIX_API_TOKEN: str
    LOANER_LAPTOP_QUESTION: str
    RENDER_TIX_SCREEN_WIDTH: int
    RENDER_TIX_SCREEN_HEIGHT: int
    RENDER_TIX_WAIT_TIMEOUT: int
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: str
    OPENAI_PROJECT_ID: str
    OPENAI_MODEL: str
    OPENAI_MODEL_CONTEXT_WINDOW: int
    OPENAI_TOKEN_COST: float
    DADLAN_WAN_API_KEY: str
    DADLAN_WAN_API_URL: str
    SUMMARISER_VAR_TEMPERATURE: str
    SUMMARISER_VAR_MAX_TOKENS: str
    SUMMARISER_VAR_MODEL: str
    SUMMARISER_VAR_PROMPT_PREFIX: str
    SUMMARISER_VAR_PROMPT_SUFFIX: str
    SUMMARISER_VAR_SPEND_HISTORY: str
    SUMMARISER_PRUNE_INTERVAL: int
    SUMMARISER_MESSAGE_AGE_THRESHOLD: int
    SUMMARISER_RESPONSE_CACHE_EXPIRY: int
    SUMMARISER_MOD_CHANNEL: int
    SUMMARISER_IGNORE_APPLICATION_MESSAGES: bool
    PRUNER_ENABLE: bool
    PRUNER_AUTOPRUNE_CHANNELS: List[int]
    PRUNER_IGNORE_MESSAGES: List[int]
    PRUNER_MESSAGE_AGE_THRESHOLD: int
    PRUNER_PRUNE_INTERVAL: int
    PRUNER_MOD_CHANNEL: int


def get_config() -> AppSettings:
    """
    Get the configuration settings based on the current config environment.
    """

    if not Path(ENV_FILENAME).exists():
        raise RuntimeError(f"Config file '{ENV_FILENAME}' does not exist.")

    load_dotenv(dotenv_path=ENV_FILENAME, override=True)

    return AppSettings()  # type: ignore
