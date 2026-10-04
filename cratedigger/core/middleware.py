import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponseBase

from cratedigger.core.request_context import request_id_var


def _resolve_request_id(raw: str | None) -> str:
    if not raw:
        return str(uuid.uuid4())

    try:
        return str(uuid.UUID(raw))
    except ValueError:
        return str(uuid.uuid4())


class RequestIdMiddleware:
    REQUEST_HEADER = "X-Request-ID"

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponseBase],
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        req_id = _resolve_request_id(request.headers.get(self.REQUEST_HEADER))

        token = request_id_var.set(req_id)

        try:
            response = self.get_response(request)

            response[self.REQUEST_HEADER] = req_id

        finally:
            request_id_var.reset(token)

        return response
