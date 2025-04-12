from flask import Flask, jsonify
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from app.database import db, init_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    from app.routes.api import api
    app.register_blueprint(api, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

    return app

app = create_app()