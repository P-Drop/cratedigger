import operator
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from config.env import EnvSettings

TEST_SECRET_KEY = "test-secret-key"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Aisla cada test del entorno de la shell: limpia las variables de EnvSettings
    y define solamente las que son necesarias"""
    for field in EnvSettings.model_fields:
        monkeypatch.delenv(field.upper(), raising=False)
    monkeypatch.setenv("DJANGO_SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a, b, c", ["a", "b", "c"]),
        ("  a,b  ", ["a", "b"]),
        ("a,,b, ,", ["a", "b"]),
        ("", []),
    ],
)
def test_allowed_hosts_parses_comma_separated_env(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: list[str]
) -> None:
    monkeypatch.setenv("ALLOWED_HOSTS", raw)

    assert EnvSettings(_env_file=None).allowed_hosts == expected


def test_allowed_hosts_keeps_list_unchanged() -> None:
    settings = EnvSettings(_env_file=None, allowed_hosts=["a", "b"])

    assert settings.allowed_hosts == ["a", "b"]


def test_allowed_hosts_defaults_to_empty_list() -> None:
    assert EnvSettings(_env_file=None).allowed_hosts == []


def test_missing_secret_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DJANGO_SECRET_KEY")

    with pytest.raises(ValidationError) as exc_info:
        EnvSettings(_env_file=None)

    errors = exc_info.value.errors()

    assert [(e["type"], e["loc"]) for e in errors] == [
        ("missing", ("django_secret_key",))
    ]


@pytest.mark.parametrize(
    "render",
    [repr, str, operator.methodcaller("model_dump_json")],
    ids=["repr", "str", "json"],
)
def test_secret_key_not_exposed_in_object_repr(
    render: Callable[[EnvSettings], str],
) -> None:
    settings = EnvSettings(_env_file=None)

    assert settings.django_secret_key.get_secret_value() == TEST_SECRET_KEY
    assert TEST_SECRET_KEY not in render(settings)


def test_debug_default_is_false() -> None:
    assert EnvSettings(_env_file=None).debug is False


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("True", True), ("true", True), ("1", True), ("False", False), ("0", False)],
)
def test_debug_parses_env_value(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool
) -> None:
    monkeypatch.setenv("DEBUG", raw)

    assert EnvSettings(_env_file=None).debug is expected


def test_unknown_key_in_env_file_is_forbidden(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_ULR=sqlite://:memory:")

    with pytest.raises(ValidationError) as exc_info:
        EnvSettings(_env_file=env_file)

    errors = exc_info.value.errors()

    assert [(e["type"], e["loc"], e["input"]) for e in errors] == [
        ("extra_forbidden", ("database_ulr",), "sqlite://:memory:")
    ]


# Prueba detalle de limitación en producción
def test_unknown_enviroment_variable_is_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEGUB", "True")

    assert EnvSettings(_env_file=None).debug is False
