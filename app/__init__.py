from flask import Flask
from .config import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    # Enable CORS for agent endpoints (adjust origins for production)
    CORS(app, resources={r"/agent/*": {"origins": "*"}})

    # ========================
    # JWT CONFIGURATION
    # ========================
    app.config["SECRET_KEY"] = "kfhsk3jh2k3hk2h3k2h3k2h3h23jh23j423423"
    app.config["JWT_SECRET_KEY"] = "Some_super_secure_and_long_base64_encoded_secret_key_for_JSWT123"
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # token không hết hạn

    jwt = JWTManager(app)

    # ========================
    # REGISTER BLUEPRINT
    # ========================
    from app.routes import agent_bp
    app.register_blueprint(agent_bp)

    return app
