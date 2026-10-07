import operator
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from config.env import EnvSettings

TEST_SECRET_KEY = "test-secret-key"
TEST_POSTGRES_PASSWORD = "test_pg_password"
TEST_MONGO_PASSWORD = "test_mongo_password"

PORT_FIELDS = ["postgres_port", "mongo_port"]

DEFAULT_POSTGRES_PORT = 5432
DEFAULT_MONGO_PORT = 27017


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Isolates each test from shell environment:
    It cleans EnvSettings vars and define required ones
    """
    for field in EnvSettings.model_fields:
        monkeypatch.delenv(field.upper(), raising=False)
    monkeypatch.setenv("DJANGO_SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setenv("POSTGRES_DB", "test_pg_db")
    monkeypatch.setenv("POSTGRES_USER", "test_pg_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", TEST_POSTGRES_PASSWORD)
    monkeypatch.setenv("MONGO_DB", "test_mongodb")
    monkeypatch.setenv("MONGO_USER", "test_mongo_user")
    monkeypatch.setenv("MONGO_PASSWORD", TEST_MONGO_PASSWORD)


# ALLOWED_HOSTS
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


# MISSING REQUIRED VARS
@pytest.mark.parametrize(
    "missing_var",
    [
        "DJANGO_SECRET_KEY",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "MONGO_DB",
        "MONGO_USER",
        "MONGO_PASSWORD",
    ],
)
def test_missing_env_var_fails_fast(
    monkeypatch: pytest.MonkeyPatch, missing_var: str
) -> None:
    monkeypatch.delenv(missing_var)

    with pytest.raises(ValidationError) as exc_info:
        EnvSettings(_env_file=None)

    errors = exc_info.value.errors()

    assert [(e["type"], e["loc"]) for e in errors] == [
        ("missing", (missing_var.lower(),))
    ]


# SECRETS
@pytest.mark.parametrize(
    ("secret", "test_value"),
    [
        ("django_secret_key", TEST_SECRET_KEY),
        ("postgres_password", TEST_POSTGRES_PASSWORD),
        ("mongo_password", TEST_MONGO_PASSWORD),
    ],
)
@pytest.mark.parametrize(
    "render",
    [repr, str, operator.methodcaller("model_dump_json")],
    ids=["repr", "str", "json"],
)
def test_secret_str_vars_not_exposed_in_object_repr(
    secret: str,
    test_value: str,
    render: Callable[[EnvSettings], str],
) -> None:
    settings = EnvSettings(_env_file=None)

    assert getattr(settings, secret).get_secret_value() == test_value
    assert test_value not in render(settings)


# DEBUG
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


# DATABASE PORT VARS
@pytest.mark.parametrize(
    ("field", "default"),
    [
        ("postgres_port", DEFAULT_POSTGRES_PORT),
        ("mongo_port", DEFAULT_MONGO_PORT),
    ],
)
def test_default_port_value(field: str, default: int) -> None:
    assert getattr(EnvSettings(_env_file=None), field) == default


@pytest.mark.parametrize(
    "field",
    PORT_FIELDS,
)
def test_valid_port_value(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    test_port_in_range = 5000
    monkeypatch.setenv(field.upper(), str(test_port_in_range))

    field_value = getattr(EnvSettings(_env_file=None), field)

    assert isinstance(field_value, int)
    assert field_value == test_port_in_range


@pytest.mark.parametrize(
    "field",
    PORT_FIELDS,
)
@pytest.mark.parametrize(
    ("raw", "error_type"),
    [
        pytest.param("0", "greater_than_equal", id="lower"),
        pytest.param("65536", "less_than_equal", id="higher"),
        pytest.param("word", "int_parsing", id="not-int"),
    ],
)
def test_invalid_port_is_rejected(
    monkeypatch: pytest.MonkeyPatch, field: str, raw: str, error_type: str
) -> None:
    monkeypatch.setenv(field.upper(), raw)

    with pytest.raises(ValidationError) as exc_info:
        EnvSettings(_env_file=None)

    errors = exc_info.value.errors()

    assert [(e["type"], e["loc"]) for e in errors] == [(error_type, (field,))]


# UNKNOWN VARS
def test_unknown_key_in_env_file_is_forbidden(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_ULR=sqlite://:memory:")

    with pytest.raises(ValidationError) as exc_info:
        EnvSettings(_env_file=env_file)

    errors = exc_info.value.errors()

    assert [(e["type"], e["loc"], e["input"]) for e in errors] == [
        ("extra_forbidden", ("database_ulr",), "sqlite://:memory:")
    ]


# Detail: test about production limitation to future consideration
def test_unknown_environment_variable_is_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEGUB", "True")

    assert EnvSettings(_env_file=None).debug is False
