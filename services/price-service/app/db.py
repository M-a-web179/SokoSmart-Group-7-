"""Database connectivity check used by the /ready endpoint."""

import logging

import psycopg

log = logging.getLogger(__name__)


def check_database(url: str, timeout: int = 3) -> bool:
    """Return True if PostgreSQL at ``url`` answers ``SELECT 1``.

    Never logs the URL itself, because it contains the password.
    Only the error type is logged.
    """
    try:
        with psycopg.connect(url, connect_timeout=timeout) as conn:
            conn.execute("SELECT 1")
    except (psycopg.Error, OSError) as err:
        log.warning("database check failed", extra={"error_type": type(err).__name__})
        return False
    return True
