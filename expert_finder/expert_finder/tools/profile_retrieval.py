"""Profile retrieval tool stub."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from expert_finder.expert_finder.tools.data import CVS
from expert_finder.expert_finder.types.schemas import CV


@dataclass(frozen=True)
class ProfileRetrievalTool:
    """Retrieve a candidate CV by ID.

    TODO: Replace with profile store / document service.
    """

    def get_cv(self, candidate_name: str) -> CV:
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug("Retrieving CV for candidate_name=%s", candidate_name)
        if candidate_name not in CVS:
            raise KeyError(f"CV not found for candidate_name={candidate_name}")
        return CVS[candidate_name]
