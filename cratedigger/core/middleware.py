import logging
import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponseBase

from cratedigger.core.request_context import request_id_var

logger = logging.getLogger(__name__)


def resolve_request_id(raw: str | None) -> str:
    """
    Return the canonical form of a valid UUID,
    or a new uuid4 otherwise.
    """
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
        req_id = resolve_request_id(request.headers.get(self.REQUEST_HEADER))

        token = request_id_var.set(req_id)

        try:
            t_before = time.perf_counter()
            response = self.get_response(request)
            t_after = time.perf_counter()

            response[self.REQUEST_HEADER] = req_id

            logger.info(
                "%s %r %s %.1fms",
                request.method,
                request.path,
                response.status_code,
                (t_after - t_before) * 1000,
            )

        finally:
            request_id_var.reset(token)

        return response
