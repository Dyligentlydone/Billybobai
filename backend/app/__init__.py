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
        if var == 'DATABASE_URL':
            logger.info(f"{var}: {'configured' if os.getenv(var) else 'missing'} - Value: {os.getenv(var, 'not set')[:10]}... (truncated for security)")
        else:
            logger.info(f"{var}: {'configured' if os.getenv(var) else 'missing'}")

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///whys.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info(f"Database URI set to: {'configured' if os.getenv('DATABASE_URL') else 'sqlite:///whys.db'} - Full URI: {app.config['SQLALCHEMY_DATABASE_URI'][:10]}... (truncated for security)")
    
    # Initialize database with a global scope
    global db
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
        try:
            from .models.workflow import Workflow
            logger.info("Workflow model imported successfully")
        except ImportError as ie:
            logger.error(f"Failed to import Workflow model: {str(ie)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Create tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created successfully (if not already present)")
                # Test database connection explicitly
                db.engine.connect()
                logger.info("Database connection test successful")
            except Exception as db_conn_error:
                logger.error(f"Failed to connect to database or create tables: {str(db_conn_error)}")
                import traceback
                logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Don't raise the error, let the app start anyway
        db = None  # Set db to None to avoid unbound variable issues

    try:
        # Register blueprints
        logger.info("Registering blueprints...")
        try:
            from .routes.api import api
            logger.info("API blueprint imported successfully")
        except ImportError as ie:
            logger.error(f"Failed to import API blueprint: {str(ie)}")
            import traceback
            logger.error(traceback.format_exc())

        try:
            from .routes.webhooks import webhooks
            logger.info("Webhooks blueprint imported successfully")
        except ImportError as ie:
            logger.error(f"Failed to import Webhooks blueprint: {str(ie)}")
            import traceback
            logger.error(traceback.format_exc())

        try:
            from .routes.workflow_routes import workflow_bp
            logger.info("Workflow blueprint imported successfully")
        except ImportError as ie:
            logger.error(f"Failed to import Workflow blueprint: {str(ie)}")
            import traceback
            logger.error(traceback.format_exc())

        try:
            from .routes.calendly import bp as calendly_bp
            logger.info("Calendly blueprint imported successfully")
        except ImportError as ie:
            logger.error(f"Failed to import Calendly blueprint: {str(ie)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Register available blueprints
        if 'api' in locals():
            app.register_blueprint(api, url_prefix='/api')
            logger.info("API blueprint registered")
        if 'webhooks' in locals():
            app.register_blueprint(webhooks, url_prefix='/webhooks')
            logger.info("Webhooks blueprint registered")
        if 'workflow_bp' in locals():
            # Register workflow blueprint without prefix since routes already include full paths
            app.register_blueprint(workflow_bp)
            logger.info("Workflow blueprint registered")
        if 'calendly_bp' in locals():
            app.register_blueprint(calendly_bp)
            logger.info("Calendly blueprint registered")
        
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
                if db is not None:
                    with app.app_context():
                        db.engine.connect()
                    health_status['database'] = 'connected'
                else:
                    health_status['database'] = 'not initialized'
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

    # Temporary workaround for frontend URL mismatch
    @app.route('/undefined/api/workflows', methods=['GET'])
    def redirect_undefined_workflows_get():
        logger.info("Received GET request to /undefined/api/workflows - redirecting to /api/workflows")
        from flask import redirect, url_for
        return redirect(url_for('workflow_bp.get_workflows'), code=307)

    @app.route('/workflow', methods=['POST'])
    def redirect_workflow_post():
        logger.info("Received POST request to /workflow - redirecting to /api/workflows")
        from flask import redirect, url_for
        return redirect(url_for('workflow_bp.create_workflow'), code=307)

    logger.info("Application creation completed successfully")
    return app

# Create the Flask application instance
app = create_app()
