"""GPT adapter for the LLM port."""

from __future__ import annotations

import os

from openai import OpenAI

from expert_finder.expert_finder.settings.inf import get_secret as inf_get_secret
from ..ports import LLMPort, SecretGetter


class GPTLLM(LLMPort):
    """Adapter for a GPT-style API.
    """

    def __init__(self, model: str, secret_getter: SecretGetter = inf_get_secret) -> None:
        self.model = model
        self.secret_getter = secret_getter

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        env = os.environ.get("ENVIRONMENT", "staging")
        api_key = self.secret_getter("OPENAI_KEY", env)
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""
        raise RuntimeError("No response received from the LLM.")


def main() -> None:
    llm = GPTLLM(model=os.environ.get("LLM_MODEL", "gpt-4o-mini"))
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France? Please answer in one sentence."
    result = llm.complete(system_prompt, user_prompt)
    print(result)


if __name__ == "__main__":
    main()
