from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    django_secret_key: SecretStr
    debug: bool = False
    allowed_hosts: Annotated[list[str], NoDecode] = Field(default_factory=list)
    database_url: str

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def split_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [host.strip() for host in value.split(",") if host.strip()]
        return value
