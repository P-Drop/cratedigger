from django.core.management import call_command
from django.db import connection


# Django
def test_django_check() -> None:
    call_command("check")


def test_database_backend_is_postgresql() -> None:
    assert connection.vendor == "postgresql"
