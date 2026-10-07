from collections.abc import Callable
from typing import NoReturn

import pytest
from django.db import DatabaseError, connection
from pymongo.errors import ServerSelectionTimeoutError

from cratedigger.core.health import CHECKS

SENSITIVE_DETAIL = "connection to server at secret-host:5432 failed."


def _postgres_connection_error() -> NoReturn:
    raise DatabaseError(SENSITIVE_DETAIL)


def _mongo_connection_error() -> NoReturn:
    raise ServerSelectionTimeoutError


@pytest.fixture
def sensitive_detail() -> str:
    return SENSITIVE_DETAIL


@pytest.fixture
def postgres_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(connection, "cursor", _postgres_connection_error)


@pytest.fixture
def mongo_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("cratedigger.core.mongo.get_database", _mongo_connection_error)


@pytest.fixture
def stub_services_up_except(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    def _stub(real_service: str) -> None:
        for service in CHECKS:
            if service == real_service:
                continue
            monkeypatch.setitem(CHECKS, service, lambda: True)

    return _stub
