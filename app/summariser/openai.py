from typing import Dict, List

from config import get_config
from openai import AsyncOpenAI
from dpn_pyutils.common import get_logger
from summariser.messages import num_tokens_from_messages
from summariser.schemas import OpenAIResponse

config = get_config()
log = get_logger(__name__)

class ChatGPTClient:

    client: AsyncOpenAI

    def __init__(self, model: str):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            organization=config.OPENAI_ORG_ID,
            project=config.OPENAI_PROJECT_ID,
        )

    async def call_api(
        self,
        prompt: List[Dict],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
    ) -> OpenAIResponse:
        """
        Calls the API with the supplied prompt and returns the response text.
        """

        kwargs = dict(
            model=model,
            messages=prompt,  # type: ignore
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort

        response = await self.client.chat.completions.create(**kwargs)
        log.info("OpenAI request: model=%s max_tokens=%s temperature=%s reasoning_effort=%s", model, max_tokens, temperature, reasoning_effort)

        total_tokens = 0
        completion_tokens = 0
        prompt_tokens = 0

        if response.usage is not None:
            total_tokens = response.usage.total_tokens
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens

        response_content = ""
        if (
            response.choices is not None
            and len(response.choices) > 0
            and response.choices[0].message.content is not None
        ):
            response_content = response.choices[0].message.content

        return OpenAIResponse(
            response=response_content,
            total_tokens=total_tokens,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
        )

    def estimate_token_cost(self, prompt: List[Dict], model: str) -> int:
        """
        Estimates the token cost of a prompt
        """

        num_tokens = num_tokens_from_messages(prompt, model=model)
        if num_tokens is None:
            raise ValueError("Invalid model provided for token estimation")

        return num_tokens
