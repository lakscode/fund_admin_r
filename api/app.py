from flask import Flask
from flask_cors import CORS

from db import db
from routes.auth import auth_bp
from routes.health import health_bp
from routes.roles import roles_bp
from routes.data import data_bp
from routes.command_center import cc_bp

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

app.register_blueprint(auth_bp)
app.register_blueprint(health_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(data_bp)
app.register_blueprint(cc_bp)


if __name__ == "__main__":
    try:
        db["users"].create_index("email", unique=True)
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
    app.run(debug=True, port=5000)
