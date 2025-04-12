from flask import Flask, jsonify
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from app.database import db, init_db
import os

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
    from app.routes.api import api
    from app.routes.webhooks import webhooks
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webhooks, url_prefix='/webhooks')

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

    @app.before_first_request
    def init_database():
        with app.app_context():
            db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)