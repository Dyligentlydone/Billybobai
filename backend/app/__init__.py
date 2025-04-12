from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from .routes.api import api
from .routes.webhooks import webhooks
from .database import db
from .models import email  # Import models to register them with SQLAlchemy

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webhooks, url_prefix='/webhooks')

    # Basic error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(error):
        return {"error": "Internal server error"}, 500

    return app
