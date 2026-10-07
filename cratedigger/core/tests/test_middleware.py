import uuid
from collections.abc import Callable

import pytest
from django.test.client import Client
from django.urls import reverse

from cratedigger.core.middleware import resolve_request_id
from cratedigger.core.request_context import RequestIdFilter

UNKNOWN_URL = "/no-such-path/"


class TestResolveRequestId:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            pytest.param(
                "77e3ef09-2678-46d2-a313-5d39fd444de0",
                "77e3ef09-2678-46d2-a313-5d39fd444de0",
                id="canonical",
            ),
            pytest.param(
                "77E3EF09-2678-46D2-A313-5D39FD444dE0",
                "77e3ef09-2678-46d2-a313-5d39fd444de0",
                id="uppercase",
            ),
            pytest.param(
                "{77e3ef09-2678-46d2-a313-5d39fd444de0}",
                "77e3ef09-2678-46d2-a313-5d39fd444de0",
                id="curly-braces-format",
            ),
            pytest.param(
                "urn:uuid:77e3ef09-2678-46d2-a313-5d39fd444de0",
                "77e3ef09-2678-46d2-a313-5d39fd444de0",
                id="urn-format",
            ),
        ],
    )
    def test_resolve_request_id_returns_normalized_when_valid(
        self, raw: str, expected: str
    ) -> None:
        value = resolve_request_id(raw)

        assert value == expected

    @pytest.mark.parametrize(
        "raw",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="empty"),
            pytest.param("not-valid-text", id="garbage"),
            pytest.param(
                "77e3ef09-2678-46d2-a313-5d39fd444de0\r\n", id="trailing-crlf"
            ),
            pytest.param(
                "77e3ef09-2678-46d2-a313-5d39fd444de0\r\nFAKE LOG LINE",
                id="log-injection",
            ),
        ],
    )
    def test_resolve_request_id_returns_replaced_request_id_when_not_valid(
        self,
        raw: str | None,
    ) -> None:
        value = resolve_request_id(raw)

        assert value != raw
        assert value == str(uuid.UUID(value))


class TestRequestIdMiddleware:
    def test_middleware_generates_id_when_header_missing(self, client: Client) -> None:
        response = client.get(UNKNOWN_URL)
        x_request_id = response.headers["X-Request-ID"]

        assert x_request_id == str(uuid.UUID(x_request_id))

    def test_middleware_returns_same_id_when_header_is_valid(
        self, client: Client
    ) -> None:
        valid_value = str(uuid.uuid4())

        response = client.get(UNKNOWN_URL, headers={"X-Request-ID": valid_value})
        x_request_id = response.headers["X-Request-ID"]

        assert x_request_id == valid_value

    def test_middleware_generates_new_id_when_header_is_not_valid(
        self, client: Client
    ) -> None:
        not_valid_value = "random-text"

        response = client.get(UNKNOWN_URL, headers={"X-Request-ID": not_valid_value})
        x_request_id = response.headers["X-Request-ID"]

        assert x_request_id != not_valid_value
        assert x_request_id == str(uuid.UUID(x_request_id))

    def test_request_id_appears_in_logs_from_other_modules(
        self,
        client: Client,
        caplog: pytest.LogCaptureFixture,
        stub_services_up_except: Callable[[str], None],
        postgres_fails: None,
    ) -> None:
        stub_services_up_except("postgresql")
        req_filter = RequestIdFilter()
        caplog.handler.addFilter(req_filter)
        valid_value = str(uuid.uuid4())

        client.get(reverse("healthcheck"), headers={"X-Request-ID": valid_value})
        [record] = [r for r in caplog.records if r.name == "cratedigger.core.health"]

        assert vars(record)["request_id"] == valid_value

    def test_access_log_carries_request_id(
        self,
        client: Client,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        req_filter = RequestIdFilter()
        caplog.handler.addFilter(req_filter)
        valid_value = str(uuid.uuid4())

        client.get(UNKNOWN_URL, headers={"X-Request-ID": valid_value})
        [record] = [
            r for r in caplog.records if r.name == "cratedigger.core.middleware"
        ]

        assert vars(record)["request_id"] == valid_value

    def test_access_log_protected_from_url_injection(
        self,
        client: Client,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        injection_url = "/url-injection%0d%0a"

        client.get(injection_url)
        [record] = [
            r for r in caplog.records if r.name == "cratedigger.core.middleware"
        ]
        record_msg = record.getMessage()

        assert "\n" not in record_msg
        assert "\r" not in record_msg
        assert "\\r\\n" in record_msg
