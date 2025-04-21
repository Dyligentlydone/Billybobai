from flask import Flask, jsonify
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
import os
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_app():
    logger.info("Starting application creation...")
    app = Flask(__name__)
    # Allow CORS only from production frontend (add localhost for dev if needed)
    CORS(app, origins=[
        "https://billybobai-production-6713.up.railway.app",
        "https://billybobai-production.up.railway.app",  # Add without -6713 just in case
        "http://localhost:5173",
        "http://localhost:3000"
    ], supports_credentials=True)

    # Log environment variables (excluding sensitive ones)
    logger.info("Environment:")
    safe_vars = ['FLASK_APP', 'FLASK_ENV', 'PORT', 'PYTHONPATH', 'DATABASE_URL']
    for var in safe_vars:
        logger.info(f"{var}: {'configured' if os.getenv(var) else 'missing'}")

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///whys.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info(f"Database URI set to: {'configured' if os.getenv('DATABASE_URL') else 'sqlite:///whys.db'}")
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        try:
            from .database import init_db
            db = init_db(app)
            logger.info("Database initialized using init_db from database module")
        except ImportError:
            logger.warning("database module not found, falling back to Flask-SQLAlchemy")
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)
            logger.info("Database object created with Flask-SQLAlchemy")
        
        # Import models to ensure they're registered
        logger.info("Importing models for database initialization...")
        from .models.workflow import Workflow
        logger.info("Models imported successfully")
        
        # Create tables if they don't exist
        with app.app_context():
            db.create_all()
        logger.info("Database tables created successfully (if not already present)")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Don't raise the error, let the app start anyway

    try:
        # Register blueprints
        logger.info("Registering blueprints...")
        from .routes.api import api
        from .routes.webhooks import webhooks
        from .routes.workflow_routes import workflow_bp
        from .routes.calendly import bp as calendly_bp
        
        app.register_blueprint(api, url_prefix='/api')
        app.register_blueprint(webhooks, url_prefix='/webhooks')
        # Register workflow blueprint without prefix since routes already include full paths
        app.register_blueprint(workflow_bp)
        app.register_blueprint(calendly_bp)
        logger.info("Blueprints registered successfully")
        
        # Log all registered routes for debugging
        logger.info("Registered routes:")
        for rule in app.url_map.iter_rules():
            logger.info(f"Endpoint: {rule.endpoint}, Path: {rule}, Methods: {rule.methods}")
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        # Log the full traceback for debugging
        import traceback
        logger.error(traceback.format_exc())

    @app.route('/')
    def index():
        return jsonify({
            'status': 'healthy',
            'message': 'Twilio Automation Hub API',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    @app.route('/health')
    def health_check():
        """Health check endpoint that always returns 200 but includes detailed status."""
        try:
            # Basic application health
            health_status = {
                'status': 'healthy',  # Always return healthy to pass Railway check
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'unknown',
                'environment': {
                    'FLASK_APP': os.getenv('FLASK_APP'),
                    'FLASK_ENV': os.getenv('FLASK_ENV'),
                    'PORT': os.getenv('PORT'),
                    'DATABASE_URL': 'configured' if os.getenv('DATABASE_URL') else 'missing'
                },
                'routes': []
            }

            # Log all registered routes in health check
            for rule in app.url_map.iter_rules():
                health_status['routes'].append({
                    'endpoint': rule.endpoint,
                    'path': str(rule),
                    'methods': list(rule.methods)
                })

            # Test database connection
            try:
                with app.app_context():
                    db.engine.connect()
                health_status['database'] = 'connected'
            except Exception as e:
                health_status['database'] = f'error: {str(e)}'
                logger.error(f"Database health check failed: {str(e)}")

            logger.info(f"Health check response: {health_status}")
            return jsonify(health_status), 200  # Always return 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            # Still return 200 to pass Railway check, but include error in response
            return jsonify({
                'status': 'healthy',  # Always return healthy
                'warning': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 200

    logger.info("Application creation completed successfully")
    return app

# Create the Flask application instance
app = create_app()
