import logging
from logging import Handler, LogRecord

import pytest


@pytest.fixture
def console_handler() -> Handler:
    [handler] = [h for h in logging.getLogger().handlers if h.name == "console"]

    return handler


@pytest.fixture
def record() -> LogRecord:
    return logging.makeLogRecord(
        {"msg": "test", "levelname": "INFO", "name": "cratedigger.test"}
    )


def test_django_server_logger_propagates_to_root_at_warning_level() -> None:
    server_logger = logging.getLogger("django.server")

    assert server_logger.propagate is True
    assert server_logger.level == logging.WARNING


def test_root_handler_uses_filter_and_format_when_default_request_id(
    console_handler: Handler, record: LogRecord
) -> None:
    console_handler.filter(record)
    log_line = console_handler.format(record)

    assert log_line.endswith("INFO [-] cratedigger.test: test")


def test_root_handler_uses_filter_and_format_with_active_request_id(
    console_handler: Handler, active_request_id: str, record: LogRecord
) -> None:
    console_handler.filter(record)
    log_line = console_handler.format(record)

    assert log_line.endswith(f"INFO [{active_request_id}] cratedigger.test: test")
