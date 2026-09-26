from collections.abc import Callable

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
    monkeypatch.setenv("DATABASE_URL", "sqlite://:memory:")


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
    "render", [repr, str, EnvSettings.model_dump_json], ids=["repr", "str", "json"]
)
def test_secret_key_not_exposed_in_object_repr(
    render: Callable[[EnvSettings], str],
) -> None:
    settings = EnvSettings(_env_file=None)

    assert settings.django_secret_key.get_secret_value() == TEST_SECRET_KEY
    assert TEST_SECRET_KEY not in render(settings)
