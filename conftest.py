from collections.abc import Iterator

import pytest

from cratedigger.core.request_context import request_id_var

TEST_REQUEST_ID = "abc123"


@pytest.fixture
def active_request_id() -> Iterator[str]:
    token = request_id_var.set(TEST_REQUEST_ID)

    yield TEST_REQUEST_ID

    request_id_var.reset(token)
