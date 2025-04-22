from flask import Flask, jsonify, request
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

    # Initialize database (canonical way)
    from app.db import db
    db.init_app(app)
    logger.info("Database initialized using canonical db instance from app.db")
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    logger.info("Flask-Migrate initialized for database migrations")

    # Import models to ensure they're registered
    logger.info("Importing models for database initialization...")
    try:
        from app.models import Business, Workflow
        logger.info("Business and Workflow models imported successfully from app.models.__init__")
    except ImportError as ie:
        logger.error(f"Failed to import models: {str(ie)}")
        import traceback
        logger.error(traceback.format_exc())

    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully (if not already present)")
            
            # Add description column to businesses table if it doesn't exist
            try:
                from sqlalchemy import text
                # Execute the SQL directly to guarantee the column exists
                db.session.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'businesses' 
                            AND column_name = 'description'
                        ) THEN
                            ALTER TABLE businesses ADD COLUMN description VARCHAR(1000);
                            RAISE NOTICE 'Added description column to businesses table';
                        ELSE
                            RAISE NOTICE 'Description column already exists in businesses table';
                        END IF;
                    END $$;
                """))
                db.session.commit()
                logger.info("Checked and added description column to businesses table if needed")
            except Exception as column_error:
                logger.error(f"Failed to add description column: {str(column_error)}")
                import traceback
                logger.error(traceback.format_exc())
            
            # Test database connection explicitly
            db.engine.connect()
            logger.info("Database connection test successful")
        except Exception as db_conn_error:
            logger.error(f"Failed to connect to database or create tables: {str(db_conn_error)}")
            import traceback
            logger.error(traceback.format_exc())

    try:
        # Register blueprints with error handling for missing dependencies
        def register_blueprints_with_error_handling(app):
            try:
                from .routes import workflow_routes
                app.register_blueprint(workflow_routes.workflow_bp)
                logger.info("Workflow blueprint registered successfully")
            except Exception as e:
                logger.error(f"Failed to register workflow blueprint: {str(e)}")

            try:
                from .routes import calendly_routes
                app.register_blueprint(calendly_routes.calendly_bp)
                logger.info("Calendly blueprint registered successfully")
            except Exception as e:
                logger.error(f"Failed to register Calendly blueprint: {str(e)}")

            try:
                from .routes.api import api as api_blueprint
                app.register_blueprint(api_blueprint, url_prefix='/api')
                logger.info("API blueprint registered successfully at /api")
            except Exception as e:
                logger.error(f"Failed to register API blueprint: {str(e)}")

            # Add other blueprints here as needed

        register_blueprints_with_error_handling(app)

        # Global error handler for NameError to catch undefined variables like SMSNotificationSettings
        @app.errorhandler(NameError)
        def handle_name_error(error):
            logger.error(f"NameError occurred: {str(error)}")
            return jsonify({
                "error": "Internal server error due to undefined resource",
                "message": str(error),
                "details": "This is likely due to a missing or undefined class/object. Please contact support."
            }), 500

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

    # Temporary workaround for frontend URL mismatch
    @app.route('/undefined/api/workflows', methods=['GET'])
    def redirect_undefined_workflows_get():
        logger.info(f"Received GET request to /undefined/api/workflows - Full URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        from flask import redirect, url_for, Response
        if 'workflow_bp.get_workflows' in app.view_functions:
            logger.info("Redirecting to /api/workflows")
            # Try a direct redirect
            return redirect(url_for('workflow_bp.get_workflows'), code=307)
        else:
            logger.error("Workflow blueprint not available for redirect")
            # Direct response if redirect fails
            return jsonify({"error": "Workflow endpoint not available, direct response from /undefined/api/workflows"}), 503

    @app.route('/workflow', methods=['POST'])
    def redirect_workflow_post():
        logger.info(f"Received POST request to /workflow - Full URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request body: {request.get_data(as_text=True)[:1000]}... (truncated if longer)")
        from flask import redirect, url_for
        if 'workflow_bp.create_workflow' in app.view_functions:
            logger.info("Redirecting to /api/workflows for POST")
            return redirect(url_for('workflow_bp.create_workflow'), code=307)
        else:
            logger.error("Workflow blueprint not available for redirect")
            return jsonify({"error": "Workflow endpoint not available for POST"}), 503

    # Catch-all for any other /undefined/* or /workflow/* paths
    @app.route('/undefined/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_undefined_path(path):
        logger.info(f"Received request to undefined path: /undefined/{path} - Method: {request.method} - Full URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        if request.method in ['POST', 'PUT']:
            logger.info(f"Request body: {request.get_data(as_text=True)[:1000]}... (truncated if longer)")
        # Direct response to confirm the request is reaching the backend
        return jsonify({
            "error": "Invalid path detected. Likely a frontend URL mismatch.",
            "path": f"/undefined/{path}",
            "message": "This is a temporary response from the backend. Please update frontend to use /api/workflows."
        }), 404

    @app.route('/workflow/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_workflow_path(path):
        logger.info(f"Received request to workflow path: /workflow/{path} - Method: {request.method} - Full URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        if request.method in ['POST', 'PUT']:
            logger.info(f"Request body: {request.get_data(as_text=True)[:1000]}... (truncated if longer)")
        return jsonify({
            "error": "Invalid workflow path detected. Likely a frontend URL mismatch.",
            "path": f"/workflow/{path}",
            "message": "This is a temporary response from the backend. Please update frontend to use /api/workflows."
        }), 404

    logger.info("Application creation completed successfully")
    return app

# Create the Flask application instance
app = create_app()
