from flask import Flask, jsonify
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from config.database import init_db, Base, engine
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Don't raise the error, let the app start anyway
        # The health check will still work even if DB isn't ready

    try:
        # Register blueprints
        logger.info("Registering blueprints...")
        from app.routes.api import api
        from app.routes.webhooks import webhooks
        from routes import workflows
        app.register_blueprint(api, url_prefix='/api')
        app.register_blueprint(webhooks, url_prefix='/webhooks')
        app.register_blueprint(workflows.bp)
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        # Don't raise the error, let the app start anyway

    @app.route('/')
    def index():
        return jsonify({
            'status': 'healthy',
            'message': 'Twilio Automation Hub API',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    @app.route('/health')
    def health_check():
        try:
            # Basic application health
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'unknown'
            }

            # Test database connection
            try:
                engine.connect()
                health_status['database'] = 'connected'
            except Exception as e:
                health_status['database'] = f'error: {str(e)}'
                logger.error(f"Database health check failed: {str(e)}")

            return jsonify(health_status), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)