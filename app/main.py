import logging
from pathlib import Path
from typing import Any, Dict

import better_exceptions
from dpn_pyutils.common import get_logger, initialize_logging
from dpn_pyutils.file import read_file_json

from config import get_config

# Initialize exception management and load config
better_exceptions.hook()
config = get_config()

# Initialize logging and capture warnings
logging_configuration: Dict[str, Any] = read_file_json(Path(config.LOGGING_CONFIG_FILE))
initialize_logging(logging_configuration)
logging.captureWarnings(True)
log = get_logger(config.APP_SYS_NAME)
log.info(
    "Starting '%s', running at %s %s every day",
    config.APP_SYS_NAME,
    config.SUMMARY_POST_AT_LOCALTIME,
    config.TIMEZONE,
)

# Start the application
# trunk-ignore(ruff/E402)
from bot import create_bot

client = create_bot(config)
client.run(config.DISCORD_TOKEN)

log.info("Finished running bot, exiting")
