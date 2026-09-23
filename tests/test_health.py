import pytest
from django.core.management import call_command
from django.test.client import Client
from django.urls import reverse


def test_django_check() -> None:
    call_command("check")


@pytest.mark.django_db
def test_admin_login_responde_200(client: Client) -> None:
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200
