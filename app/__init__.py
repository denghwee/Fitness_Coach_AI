from flask import Flask
from .config import *
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    # Enable CORS for agent endpoints (adjust origins for production)
    CORS(app, resources={r"/agent/*": {"origins": "*"}})

    from app.routes import agent_bp
    app.register_blueprint(agent_bp)

    return app