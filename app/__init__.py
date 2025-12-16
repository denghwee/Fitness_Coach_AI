from flask import Flask
from config import *

def create_app():
    app = Flask(__name__)

    from app.routes import agent_bp
    app.register_blueprint(agent_bp)

    return app