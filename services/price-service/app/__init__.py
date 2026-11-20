from flask import Flask

from .config import Config
from .dashboard import dashboard
from .db import check_database
from .logging_config import configure_logging, register_request_logging
from .repository import InMemoryPriceRepository
from .routes import api
from .services import PriceService
from .ussd_routes import ussd


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    configure_logging(app.config["LOG_LEVEL"])
    register_request_logging(app)

    # Swappable so tests can fake a database that is up or down
    app.config.setdefault("DB_CHECK", check_database)

    repo = InMemoryPriceRepository()
    repo.load_seed(app.config["SEED_FILE"])
    app.config["PRICE_SERVICE"] = PriceService(repo)

    app.register_blueprint(api)
    app.register_blueprint(ussd)
    app.register_blueprint(dashboard)
    return app
