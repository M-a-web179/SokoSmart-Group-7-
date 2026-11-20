"""Structured logging: one JSON object per line on stdout.

Docker captures stdout, so `docker logs` / `docker compose logs` show the
same lines, and any log tool can parse them without regexes.
"""

import json
import logging
import sys
import time
import uuid
from datetime import UTC, datetime

from flask import Flask, g, request

# Attributes every LogRecord has. Anything else came in through `extra=`.
_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # Werkzeug's own access log would duplicate ours in plain text
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def register_request_logging(app: Flask) -> None:
    access_log = logging.getLogger("price_service.access")

    @app.before_request
    def _start_timer():
        g.start_time = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    @app.after_request
    def _log_request(response):
        duration_ms = round((time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000, 2)
        response.headers["X-Request-ID"] = g.get("request_id", "")
        access_log.info(
            "request",
            extra={
                "request_id": g.get("request_id"),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
            },
        )
        return response
