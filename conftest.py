from collections.abc import Iterator

import pytest
from pymongo.database import Database
from pytest_django.fixtures import Settings

from infra.mongo import Document, get_client, get_database


@pytest.fixture
def mongo_db(settings: Settings) -> Iterator[Database[Document]]:
    test_name = f"test_{settings.MONGODB.name}"
    settings.MONGODB = settings.MONGODB.model_copy(update={"name": test_name})

    database = get_database()
    assert database.name.startswith("test_")

    yield database

    get_client().drop_database(test_name)
