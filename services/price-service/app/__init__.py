from typing import Optional

from flask import Flask

from .config import Config
from .repository import InMemoryPriceRepository
from .routes import api
from .services import PriceService


def create_app(config_overrides: Optional[dict] = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    if app.config["DATABASE_URL"]:
        # Lazy import keeps the default in-memory mode independent of psycopg.
        from .postgres_repository import PostgresPriceRepository

        repo = PostgresPriceRepository(app.config["DATABASE_URL"])

        @app.cli.command("init-db")
        def init_db():
            """Create the initial PostgreSQL schema for local development."""
            repo.initialize()
    else:
        repo = InMemoryPriceRepository()
        repo.load_seed(app.config["SEED_FILE"])
    app.config["PRICE_SERVICE"] = PriceService(repo)

    app.register_blueprint(api)
    return app
