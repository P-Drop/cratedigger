import logging
from collections.abc import Callable

import pytest
from django.test.client import Client
from django.urls import reverse

from cratedigger.core.health import _services_registry


@pytest.mark.integration
@pytest.mark.django_db
def test_health_returns_200_when_all_services_up(client: Client) -> None:
    response = client.get(reverse("healthcheck"))
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "healthy"
    assert body["checks"]["postgresql"] == "up"
    assert body["checks"]["mongodb"] == "up"


@pytest.mark.parametrize("down_service", ["postgresql", "mongodb"])
def test_health_returns_503_when_service_down(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
    down_service: str,
    stub_services_up_except: Callable[[str], None],
) -> None:
    monkeypatch.setitem(_services_registry, down_service, lambda: False)
    stub_services_up_except(down_service)

    response = client.get(reverse("healthcheck"))
    body = response.json()

    assert response.status_code == 503
    assert body["status"] == "unhealthy"
    assert body["checks"][down_service] == "down"


def test_health_rejects_post(client: Client) -> None:
    response = client.post(reverse("healthcheck"))

    assert response.status_code == 405


def test_health_does_not_leak_exception_details(
    client: Client,
    caplog: pytest.LogCaptureFixture,
    sensitive_detail: str,
    stub_services_up_except: Callable[[str], None],
    postgres_fails: None,
) -> None:
    caplog.set_level(logging.ERROR, logger="cratedigger.core.health")
    stub_services_up_except("postgresql")

    response = client.get(reverse("healthcheck"))

    assert sensitive_detail not in response.content.decode()
    assert sensitive_detail in caplog.text
    assert "PostgreSQL healthcheck failed." in caplog.records[0].message
