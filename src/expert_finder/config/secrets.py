"""Secret access helpers for runtime integrations."""

from __future__ import annotations

from functools import lru_cache

from infisical_sdk import InfisicalSDKClient

from expert_finder.config.settings import get_infisical_settings

@lru_cache(maxsize=1)
def _get_client() -> InfisicalSDKClient:
    settings = get_infisical_settings()
    client = InfisicalSDKClient(host=settings.host)
    client.auth.universal_auth.login(settings.user, settings.key)
    return client


def get_secret(name: str) -> str:
    settings = get_infisical_settings()
    value = _get_client().secrets.get_secret_by_name(
        name,
        project_id=settings.project_id,
        environment_slug=settings.environment_slug,
        secret_path="/",
    )
    return value.secretValue

