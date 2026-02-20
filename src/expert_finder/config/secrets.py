"""Secret access helpers for runtime integrations."""

from __future__ import annotations

from dotenv import load_dotenv
from infisical_sdk import InfisicalSDKClient

from expert_finder.config.settings import get_infisical_settings

_client: InfisicalSDKClient | None = None


def _get_client() -> InfisicalSDKClient:
    global _client
    if _client is None:
        load_dotenv()
        settings = get_infisical_settings()
        client = InfisicalSDKClient(host=settings.host)
        client.auth.universal_auth.login(settings.user, settings.key)
        _client = client
    return _client


def get_secret(name: str, env: str) -> str:
    settings = get_infisical_settings()
    value = _get_client().secrets.get_secret_by_name(
        name,
        project_id=settings.project_id,
        environment_slug=env,
        secret_path="/",
    )
    return value.secretValue

