from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # CORS
    CORS(app, resources={r"/agent/*": {"origins": "*"}})

    # EXTENSIONS
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # IMPORT MODELS (CHỈ Ở ĐÂY)
    from app import models

    from app.routes.agent_routes import agent_bp
    app.register_blueprint(agent_bp)

    return app
