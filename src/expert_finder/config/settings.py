"""Typed runtime settings shared across entrypoints."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SupportedModel(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_5_2 = "gpt-5.2"


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["local", "production"] = Field(alias="API_ENVIRONMENT")
    cookie_secure: bool = Field(alias="COOKIE_SECURE")
    backend: Literal["sqlalchemy"] = Field(alias="EXPERT_FINDER_BACKEND")
    app_test_password: str = Field(alias="APP_TEST_PASSWORD")
    oauth2_secret_key: str = Field(alias="OAUTH2_SECRET_KEY")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0)
    expert_finder_db_path: Path | None = Field(default=None, alias="EXPERT_FINDER_DB_PATH")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    @model_validator(mode="after")
    def validate_db_source(self) -> ApiSettings:
        if self.environment == "local" and self.expert_finder_db_path is None:
            raise ValueError("EXPERT_FINDER_DB_PATH is required when API_ENVIRONMENT=local")
        if self.environment == "production" and not self.database_url:
            raise ValueError("DATABASE_URL is required when API_ENVIRONMENT=production")
        return self

    @property
    def question_logs_db_url(self) -> str:
        if self.environment == "local":
            return f"sqlite+pysqlite:///{self.expert_finder_db_path}"
        return self.database_url  # validated above


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    gpt_model: SupportedModel = Field(default=SupportedModel.GPT_5_2, alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.0, alias="LLM_TEMPERATURE", ge=0.0, le=1.0)
    search_top_k: int = Field(default=5, alias="SEARCH_TOP_K", gt=0)


class InfisicalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    user: str = Field(alias="INFISICAL_USER")
    key: str = Field(alias="INFISICAL_KEY")
    project_id: str = Field(alias="INFISICAL_PROJECT_ID")
    environment_slug: str = Field(default="staging", alias="INFISICAL_ENVIRONMENT")
    host: str = Field(default="https://app.infisical.com", alias="INFISICAL_HOST")


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    return ApiSettings()


@lru_cache(maxsize=1)
def get_agent_settings() -> AgentSettings:
    return AgentSettings()


@lru_cache(maxsize=1)
def get_infisical_settings() -> InfisicalSettings:
    return InfisicalSettings()
