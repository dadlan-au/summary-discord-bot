from typing import Dict, List

from config import get_config
from openai import OpenAI
from summariser.messages import num_tokens_from_messages
from summariser.schemas import OpenAIResponse

config = get_config()


class ChatGPTClient:

    client: OpenAI

    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            organization=config.OPENAI_ORG_ID,
            project=config.OPENAI_PROJECT_ID,
        )

    def call_api(
        self,
        prompt: List[Dict],
        max_tokens: int = 150,
        temperature: float = 0.7,
    ) -> OpenAIResponse:
        """
        Calls the API with the supplied prompt and returns the response text.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=prompt,  # type: ignore
            max_tokens=max_tokens,
            temperature=temperature,
        )

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
