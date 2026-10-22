import os


class Config:
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SEED_FILE = os.getenv("SEED_FILE", "data/seed_prices.json")
