"""GPT adapter for the LLM port."""

from __future__ import annotations

from openai import OpenAI

from expert_finder.config.secrets import get_secret as inf_get_secret
from expert_finder.domain.ports import LLMPort, SecretGetter


class GPTLLM(LLMPort):
    """Adapter for a GPT-style API.
    """

    def __init__(
        self,
        model: str,
        secret_getter: SecretGetter = inf_get_secret,
    ) -> None:
        self.model = model
        self.secret_getter = secret_getter
        api_key = self.secret_getter("OPENAI_KEY")
        self._client = OpenAI(api_key=api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""
        raise RuntimeError("No response received from the LLM.")