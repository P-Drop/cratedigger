import logging
from collections.abc import Callable

import pymongo
from django.db import connection, transaction

from . import mongo

logger = logging.getLogger(__name__)


def _healthcheck_postgres() -> bool:
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '2s'")
            cursor.execute("SELECT 1;")
            cursor.fetchone()

        return True

    except Exception:
        logger.exception("PostgreSQL healthcheck failed.")
        return False


def _healthcheck_mongo() -> bool:
    try:
        with pymongo.timeout(2):
            mongo_database = mongo.get_database()
            mongo_database.command("ping")

        return True

    except Exception:
        logger.exception("MongoDB healthcheck failed.")
        return False


# Dependency checks run by run_checks()
# Tests replace entries with monkeypatch.setitem
CHECKS: dict[str, Callable[[], bool]] = {
    "postgresql": _healthcheck_postgres,
    "mongodb": _healthcheck_mongo,
}


def run_checks() -> dict[str, bool]:
    return {service: healthcheck() for service, healthcheck in CHECKS.items()}
