import os


class Config:
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SEED_FILE = os.getenv("SEED_FILE", "data/seed_prices.json")

    # PostgreSQL connection string, e.g. postgresql://user:pass@host:5432/sokosmart
    # Comes from the environment only (Ansible/.env on the VM), never from code.
    # Empty means "no database configured" and /ready skips the DB check.
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "3"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
