import os
import argparse

# Parse --env before any config imports
parser = argparse.ArgumentParser()
parser.add_argument("--env", default="development", choices=["development", "test", "production"])
args, _ = parser.parse_known_args()
os.environ["FLASK_ENV"] = args.env

from flask import Flask
from flask_cors import CORS

from config import CORS_ORIGINS, DEBUG, PORT, ENV
from db import db
from routes.auth import auth_bp
from routes.health import health_bp
from routes.roles import roles_bp
from routes.data import data_bp
from routes.command_center import cc_bp

app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)

app.register_blueprint(auth_bp)
app.register_blueprint(health_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(data_bp)
app.register_blueprint(cc_bp)


if __name__ == "__main__":
    try:
        db["users"].create_index("email", unique=True)
        print(f"[{ENV}] Connected to MongoDB successfully")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
    print(f"Starting server in {ENV} mode on port {PORT}")
    app.run(debug=DEBUG, port=PORT)
