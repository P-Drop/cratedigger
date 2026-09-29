import pytest
from django.core.management import call_command
from django.db import connection
from django.test.client import Client
from django.urls import reverse
from pymongo.database import Database

from cratedigger.core.mongo import Document


# Django
def test_django_check() -> None:
    call_command("check")


# Postgres
@pytest.mark.django_db
def test_admin_login_returns_200(client: Client) -> None:
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200


def test_database_backend_is_postgresql() -> None:
    assert connection.vendor == "postgresql"


@pytest.mark.django_db
def test_postgres_responds() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


# Mongo DB
def test_mongo_responds(mongo_db: Database[Document]) -> None:
    assert mongo_db.command("ping")["ok"] == 1
