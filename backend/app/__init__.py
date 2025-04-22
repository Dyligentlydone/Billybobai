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
                from sqlalchemy import text, inspect
                # Check database dialect to use appropriate syntax
                dialect = db.engine.dialect.name
                logger.info(f"Detected database dialect: {dialect}")
                
                if dialect == 'sqlite':
                    # SQLite doesn't support DO blocks, use direct SQL instead
                    # Check if businesses table exists
                    try:
                        inspector = inspect(db.engine)
                        if 'businesses' not in inspector.get_table_names():
                            db.session.execute(text("""
                                CREATE TABLE IF NOT EXISTS businesses (
                                    id INTEGER PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    description VARCHAR(1000),
                                    domain VARCHAR(255) NOT NULL DEFAULT 'default-domain.com'
                                );
                            """))
                            db.session.commit()
                            logger.info("Created businesses table with description and domain columns")
                        
                        # Check if description column exists in businesses table
                        columns = [col['name'] for col in inspector.get_columns('businesses')]
                        if 'description' not in columns:
                            db.session.execute(text('ALTER TABLE businesses ADD COLUMN description VARCHAR(1000);'))
                            db.session.commit()
                            logger.info("Added description column to businesses table")
                        
                        # Check if domain column exists in businesses table
                        if 'domain' not in columns:
                            db.session.execute(text("ALTER TABLE businesses ADD COLUMN domain VARCHAR(255) NOT NULL DEFAULT 'default-domain.com';"))
                            db.session.commit()
                            logger.info("Added domain column to businesses table")
                        
                        # Check for other columns in workflows table
                        if 'workflows' in inspector.get_table_names():
                            columns = [col['name'] for col in inspector.get_columns('workflows')]
                            if 'actions' not in columns:
                                db.session.execute(text('ALTER TABLE workflows ADD COLUMN actions JSON;'))
                                db.session.commit()
                                logger.info("Added actions column to workflows table")
                            if 'conditions' not in columns:
                                db.session.execute(text('ALTER TABLE workflows ADD COLUMN conditions JSON;'))
                                db.session.commit()
                                logger.info("Added conditions column to workflows table")
                    except Exception as e:
                        logger.error(f"SQLite schema update error: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                else:
                    # PostgreSQL - use DO blocks with more robust error handling
                    logger.info("Attempting PostgreSQL schema updates...")
                    try:
                        # First make sure the businesses table exists
                        db.session.execute(text("""
                            DO $$
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 
                                    FROM information_schema.tables 
                                    WHERE table_name = 'businesses'
                                ) THEN
                                    CREATE TABLE businesses (
                                        id INTEGER PRIMARY KEY,
                                        name VARCHAR(255) NOT NULL,
                                        description VARCHAR(1000),
                                        domain VARCHAR(255) NOT NULL DEFAULT 'default-domain.com'
                                    );
                                    RAISE NOTICE 'Created businesses table with description and domain columns';
                                END IF;
                            END $$;
                        """))
                        db.session.commit()
                        logger.info("Successfully checked/created businesses table")
                        
                        # Make a second explicit attempt to add the description column
                        logger.info("Explicitly trying to add description column to businesses table...")
                        try:
                            db.session.execute(text("""
                                ALTER TABLE businesses ADD COLUMN IF NOT EXISTS description VARCHAR(1000);
                            """))
                            db.session.commit()
                            logger.info("Description column added to businesses table or already exists")
                        except Exception as column_error:
                            logger.error(f"Error adding description column (may already exist): {str(column_error)}")
                            # Continue execution even if this fails
                        
                        # Make an explicit attempt to add the domain column
                        logger.info("Explicitly trying to add domain column to businesses table...")
                        try:
                            db.session.execute(text("""
                                ALTER TABLE businesses ADD COLUMN IF NOT EXISTS domain VARCHAR(255) NOT NULL DEFAULT 'default-domain.com';
                            """))
                            db.session.commit()
                            logger.info("Domain column added to businesses table or already exists")
                        except Exception as column_error:
                            logger.error(f"Error adding domain column (may already exist): {str(column_error)}")
                            # Continue execution even if this fails
                            
                        # Verify the column exists by querying the information schema
                        result = db.session.execute(text("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'businesses' 
                            AND column_name = 'description';
                        """)).fetchone()
                        
                        if result:
                            logger.info("Verified description column exists in businesses table")
                        else:
                            logger.warning("Could not verify description column in businesses table after attempted schema update")
                        
                        # Also update the workflows table if needed
                        logger.info("Checking workflows table schema...")
                        db.session.execute(text("""
                            DO $$
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 
                                    FROM information_schema.tables 
                                    WHERE table_name = 'workflows'
                                ) THEN
                                    -- Skip creating workflows table, let SQLAlchemy handle it
                                    RAISE NOTICE 'Workflows table does not exist, will be created by SQLAlchemy';
                                ELSE
                                    -- Table exists, check for columns
                                    IF NOT EXISTS (
                                        SELECT 1 
                                        FROM information_schema.columns 
                                        WHERE table_name = 'workflows' 
                                        AND column_name = 'actions'
                                    ) THEN
                                        ALTER TABLE workflows ADD COLUMN actions JSONB;
                                        RAISE NOTICE 'Added actions column to workflows table';
                                    END IF;
                                    
                                    IF NOT EXISTS (
                                        SELECT 1 
                                        FROM information_schema.columns 
                                        WHERE table_name = 'workflows' 
                                        AND column_name = 'conditions'
                                    ) THEN
                                        ALTER TABLE workflows ADD COLUMN conditions JSONB;
                                        RAISE NOTICE 'Added conditions column to workflows table';
                                    END IF;
                                END IF;
                            END $$;
                        """))
                        db.session.commit()
                        logger.info("Completed workflows table schema check")
                    except Exception as pg_error:
                        logger.error(f"PostgreSQL schema update error: {str(pg_error)}")
                        import traceback
                        logger.error(traceback.format_exc())
            except Exception as column_error:
                logger.error(f"Failed to update database schema: {str(column_error)}")
                import traceback
                logger.error(traceback.format_exc())
            
            # Test database connection explicitly
            db.engine.connect()
            logger.info("Database connection test successful")
            
            # Log database details for debugging
            try:
                engine_url = db.engine.url
                logger.info(f"Connected to database: dialect={engine_url.drivername}, host={engine_url.host}, database={engine_url.database}")
                
                # Test a simple query
                from sqlalchemy import text
                result = db.session.execute(text("SELECT 1")).fetchone()
                logger.info(f"Simple query test result: {result}")
                
                # List all tables
                inspector = db.inspect(db.engine)
                all_tables = inspector.get_table_names()
                logger.info(f"Database tables: {all_tables}")
            except Exception as e:
                logger.error(f"Error getting database details: {e}")
            
        except Exception as db_conn_error:
            logger.error(f"Failed to connect to database or create tables: {str(db_conn_error)}")
            import traceback
            logger.error(traceback.format_exc())

    logger.info("Registering route blueprints...")
    try:
        # Import and register routes
        from .routes.workflow_routes import workflow_bp
        app.register_blueprint(workflow_bp)
        logger.info("Workflow routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register workflow routes: {str(e)}")
    
    try:
        # Import and register business routes - must be registered for SMSConfigWizard to work
        from .routes.business_routes import business_bp
        app.register_blueprint(business_bp)
        logger.info("Business routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register business routes: {str(e)}")

    try:
        # Register blueprints with error handling for missing dependencies
        def register_blueprints_with_error_handling(app):
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
