import logging
from collections.abc import Iterator

import pytest

from cratedigger.core.request_context import RequestIdFilter, request_id_var

TEST_REQUEST_ID = "abc123"


@pytest.fixture
def active_request_id() -> Iterator[str]:
    token = request_id_var.set(TEST_REQUEST_ID)

    yield TEST_REQUEST_ID

    request_id_var.reset(token)


def test_filter_sets_default_request_id() -> None:
    record = logging.makeLogRecord({"msg": "test"})

    log_filter = RequestIdFilter()
    log_filter_applied = log_filter.filter(record)

    assert log_filter_applied is True
    assert vars(record)["request_id"] == "-"


def test_filter_sets_active_request_id(active_request_id: str) -> None:
    record = logging.makeLogRecord({"msg": "test"})

    log_filter = RequestIdFilter()
    log_filter_applied = log_filter.filter(record)

    assert log_filter_applied is True
    assert vars(record)["request_id"] == active_request_id
