from datetime import datetime
from typing import Dict, List

import tiktoken
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


# def num_tokens_from_messages_legacy(messages, model="gpt-3.5-turbo-0613"):
#     """
#     Return the number of tokens used by a list of messages.
#     """

#     try:
#         encoding = tiktoken.encoding_for_model(model)
#     except KeyError:
#         print("Warning: model not found. Using cl100k_base encoding.")
#         encoding = tiktoken.get_encoding("cl100k_base")

#     if model in [
#         "gpt-3.5-turbo-0613",
#         "gpt-3.5-turbo-16k-0613",
#         "gpt-4-0314",
#         "gpt-4-32k-0314",
#         "gpt-4-0613",
#         "gpt-4-32k-0613",
#     ]:
#         tokens_per_message = 3
#         tokens_per_name = 1
#     elif model in ["gpt-3.5-turbo-0301", "gpt-3.5-turbo-0125"]:
#         tokens_per_message = (
#             4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
#         )
#         tokens_per_name = -1  # if there's a name, the role is omitted
#     elif "gpt-3.5-turbo" in model:
#         print(
#             "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
#         )
#         return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
#     elif "gpt-4" in model:
#         print(
#             "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
#         )
#         return num_tokens_from_messages(messages, model="gpt-4-0613")
#     else:
#         raise NotImplementedError(
#             f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
#         )
#     num_tokens = 0
#     for message in messages:
#         num_tokens += tokens_per_message
#         for key, value in message.items():
#             num_tokens += len(encoding.encode(value))
#             if key == "name":
#                 num_tokens += tokens_per_name

#     num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
#     return num_tokens
