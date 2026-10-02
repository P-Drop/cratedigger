from collections.abc import Callable

from cratedigger.core.health import run_checks


def test_run_checks_reports_postgres_down_on_database_error(
    stub_services_up_except: Callable[[str], None],
    postgres_fails: None,
) -> None:
    stub_services_up_except("postgresql")

    assert run_checks()["postgresql"] is False


def test_run_checks_reports_mongo_down_on_database_error(
    stub_services_up_except: Callable[[str], None], mongo_fails: None
) -> None:
    stub_services_up_except("mongodb")

    assert run_checks()["mongodb"] is False
