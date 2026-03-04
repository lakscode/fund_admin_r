import os
import importlib

ENV = os.getenv("FLASK_ENV", "development")

_module = importlib.import_module(f"config.{ENV}")

MONGO_URI = _module.MONGO_URI
MONGO_DB_NAME = _module.MONGO_DB_NAME
JWT_SECRET_KEY = _module.JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES_HOURS = _module.JWT_ACCESS_TOKEN_EXPIRES_HOURS
DEBUG = _module.DEBUG
PORT = _module.PORT
CORS_ORIGINS = _module.CORS_ORIGINS
