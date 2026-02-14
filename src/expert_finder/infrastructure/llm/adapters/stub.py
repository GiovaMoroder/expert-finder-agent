"""Deterministic stub LLM for local development."""

from __future__ import annotations

import json
import re
from typing import Any

from expert_finder.domain.ports import LLMPort


class DeterministicStubLLM(LLMPort):
    """A deterministic, heuristic-based stand-in for an LLM.

    This keeps the POC runnable without external services.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        schema_name = self._infer_schema_name(system_prompt)
        payload = self._extract_payload(user_prompt)

        if schema_name == "QueryExtraction":
            return json.dumps(self._extract_query(system_prompt, user_prompt))
        if schema_name == "ShortlistResult":
            return json.dumps(self._shortlist(payload))
        if schema_name == "FinalResult":
            return json.dumps(self._compare(payload))

        raise ValueError(f"Unsupported schema in stub LLM: {schema_name}")

    @staticmethod
    def _infer_schema_name(system_prompt: str) -> str:
        match = re.search(r"Schema:\s*(\w+)", system_prompt)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_payload(user_prompt: str) -> dict[str, Any]:
        marker = "PAYLOAD:"
        if marker not in user_prompt:
            return {}
        payload_str = user_prompt.split(marker, 1)[1].strip()
        return json.loads(payload_str)

    @staticmethod
    def _extract_query(system_prompt: str, question: str) -> dict[str, Any]:
        text = question.strip()
        institution = DeterministicStubLLM._find_institution(text) or "Unknown"
        tool_required = institution != "Unknown"
        default_filter_column = "company" if "professional experience" in system_prompt.lower() else "institution"
        return {
            "tool_required": tool_required,
            "filter_column": default_filter_column if tool_required else None,
            "filter_value": institution if tool_required else None,
            "ranking": None,
            "sort_by": None,
            "sort_order": None,
        }

    @staticmethod
    def _find_institution(text: str) -> str | None:
        patterns = [
            r"at\s+([A-Z][\w&.,\- ]+)",
            r"from\s+([A-Z][\w&.,\- ]+)",
            r"in\s+([A-Z][\w&.,\- ]+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                institution = match.group(1).strip().rstrip("?.,")
                institution = re.split(r"\s+in\s+role\s+|\s+as\s+|\s+with\s+", institution, maxsplit=1)[0]
                return institution.strip()
        return None

    @staticmethod
    def _shortlist(payload: dict[str, Any]) -> dict[str, Any]:
        candidates = payload.get("candidates", [])
        selected = candidates[:7]
        return {"candidate_names": selected}

    @staticmethod
    def _compare(payload: dict[str, Any]) -> dict[str, Any]:
        profiles = payload.get("profiles", [])
        top_names = [profile.get("name") for profile in profiles][:3]
        experts = []
        for candidate_name in top_names:
            experts.append(
                {
                    "name": candidate_name,
                    "reason": "Selected based on available profile signals and relevance to the query.",
                }
            )

        return {"experts": experts}
