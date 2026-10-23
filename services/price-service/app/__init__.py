from flask import Flask

from .config import Config
from .repository import InMemoryPriceRepository
from .routes import api
from .services import PriceService
from .ussd_routes import ussd


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    repo = InMemoryPriceRepository()
    repo.load_seed(app.config["SEED_FILE"])
    app.config["PRICE_SERVICE"] = PriceService(repo)

    app.register_blueprint(api)
    app.register_blueprint(ussd)
    return app
