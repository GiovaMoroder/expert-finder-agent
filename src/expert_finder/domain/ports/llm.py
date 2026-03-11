"""LLM port (interface) for adapters."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

SecretGetter = Callable[[str], str]


class LLMPort(ABC):
    """Port interface for LLM implementations."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return a JSON string payload.

        The JSON must conform to the expected schema described in the prompt.
        """

    def call_json(self, schema: Type[BaseModel], system_prompt: str, user_prompt: str) -> BaseModel:
        """Call the LLM and validate the JSON response using Pydantic."""
        logger = logging.getLogger(self.__class__.__name__)
        
        raw = self.complete(system_prompt, user_prompt)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Raw LLM response:\n%s", raw)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1 :]
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3]
        data = json.loads(cleaned)
        try:
            return schema.model_validate(data)
        except Exception:
            if schema.__name__ == "ShortlistResult" and isinstance(data, dict):
                names = data.get("candidate_names")
                if isinstance(names, list) and len(names) > 7:
                    data["candidate_names"] = names[:7]
                    return schema.model_validate(data)
            raise
