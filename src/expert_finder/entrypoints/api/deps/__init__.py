"""Shared dependencies for API routers.

This module is intentionally a small facade over split submodules:
- agent wiring
- credential validation
- token/JWT helpers
- FastAPI auth dependencies

Import from here to keep call sites stable:
`from expert_finder.entrypoints.api.deps import require_bearer_user, get_agent, ...`
"""

from __future__ import annotations

from expert_finder.entrypoints.api.deps.agent import get_agent_cached
from expert_finder.entrypoints.api.deps.auth import (
    current_user,
    oauth2_scheme,
    require_bearer_user,
)
from expert_finder.entrypoints.api.deps.credentials import (
    USERNAME_REGEX,
    validate_credentials,
)
from expert_finder.entrypoints.api.deps.tokens import (
    OAUTH2_ALGORITHM,
    issue_access_token,
)
from expert_finder.entrypoints.api.deps.persistence import (
    get_expert_feedback_repository_cached,
    get_question_log_repository_cached,
    get_question_feedback_repository_cached,
)

__all__ = [
    "OAUTH2_ALGORITHM",
    "USERNAME_REGEX",
    "issue_access_token",
    "current_user",
    "get_agent_cached",
    "get_expert_feedback_repository_cached",
    "get_question_feedback_repository_cached",
    "get_question_log_repository_cached",
    "oauth2_scheme",
    "require_bearer_user",
    "validate_credentials",
]
