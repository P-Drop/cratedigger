from functools import cache
from typing import Any

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database

type Document = dict[str, Any]


@cache
def get_client() -> MongoClient[Document]:
    config = settings.MONGODB
    return MongoClient(
        username=config.user,
        password=config.password.get_secret_value(),
        host=config.host,
        port=config.port,
        authSource="admin",
        tz_aware=True,
        uuidRepresentation="standard",
        serverSelectionTimeoutMS=5000,
    )


def get_database() -> Database[Document]:
    return get_client()[settings.MONGODB.name]
