from flask import Flask, jsonify
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from config.database import init_db, Base, engine
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize database
    init_db()

    # Register blueprints
    from app.routes.api import api
    from app.routes.webhooks import webhooks
    from routes import workflows
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webhooks, url_prefix='/webhooks')
    app.register_blueprint(workflows.bp)

    @app.route('/')
    def index():
        return jsonify({
            'status': 'healthy',
            'message': 'Twilio Automation Hub API',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)