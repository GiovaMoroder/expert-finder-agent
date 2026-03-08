"""LLM port (interface) for adapters."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Type

from pydantic import BaseModel, TypeAdapter

SecretGetter = Callable[[str], str]


class LLMPort(ABC):
    """Port interface for LLM implementations."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return a JSON string payload.

        The JSON must conform to the expected schema described in the prompt.
        """

    @staticmethod
    def _decode_json_payload(raw: str, logger: logging.Logger) -> object:
        cleaned = raw.strip()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Raw LLM response:\n%s", raw)
        if cleaned.startswith("```"):
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1 :]
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3]
        return json.loads(cleaned)

    def call_json(self, schema: Type[BaseModel], system_prompt: str, user_prompt: str) -> BaseModel:
        """Call the LLM and validate the JSON response using Pydantic."""
        logger = logging.getLogger(self.__class__.__name__)
        data = self._decode_json_payload(self.complete(system_prompt, user_prompt), logger)
        try:
            return schema.model_validate(data)
        except Exception:
            if schema.__name__ == "ShortlistResult" and isinstance(data, dict):
                names = data.get("candidate_names")
                if isinstance(names, list) and len(names) > 7:
                    data["candidate_names"] = names[:7]
                    return schema.model_validate(data)
            raise

    def call_json_list(self, schema: Type[BaseModel], system_prompt: str, user_prompt: str) -> list[BaseModel]:
        """Call the LLM and validate a JSON array of schema objects."""
        logger = logging.getLogger(self.__class__.__name__)
        data = self._decode_json_payload(self.complete(system_prompt, user_prompt), logger)
        adapter = TypeAdapter(list[schema])
        return adapter.validate_python(data)
