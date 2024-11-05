from datetime import datetime
from typing import Dict, List

from dpn_pyutils.common import get_logger
from tokencost import count_message_tokens

log = get_logger(__name__)


def format_messages_for_summary(messages: List[Dict]) -> str:
    """
    Formats messages into a string for summarization by ChatGPT.
    """

    sorted_messages = sorted(messages, key=lambda x: x["timestamp"])
    formatted_messages = []
    for msg in sorted_messages:
        timestamp = datetime.fromtimestamp(msg["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        formatted_messages.append(f"{timestamp} - {msg['name']}: {msg['message']}")

    concatenated_messages = "\n".join(formatted_messages)

    return concatenated_messages


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613") -> int:
    """
    Return the number of tokens used by a list of messages.
    """

    log.debug("Calculating token cost for messages using model '%s'", model)
    prompt_cost = count_message_tokens(messages, model)

    log.debug("Prompt estimated token cost: %s", prompt_cost)

    return prompt_cost
