from flask import Flask, jsonify, request
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
import os
import logging
import sys
import importlib
import traceback
import json

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
    # Allow CORS with proper headers for Authentication
    CORS(app, 
         resources={r"/api/*": {
             "origins": [
                 "https://billybobai-production-6713.up.railway.app",
                 "https://billybobai-production.up.railway.app",
                 "http://localhost:5173",
                 "http://localhost:3000",
                 "http://127.0.0.1:5173",
                 "http://127.0.0.1:3000"
             ]
         }},
         supports_credentials=False,  # Changed to avoid preflight issues
         allow_headers=["Content-Type", "Authorization", "Accept"])

    # Log environment variables (excluding sensitive ones)
    logger.info("Environment:")
    safe_vars = ['FLASK_APP', 'FLASK_ENV', 'PORT', 'PYTHONPATH', 'DATABASE_URL']
    for var in safe_vars:
        if var == 'DATABASE_URL':
            logger.info(f"{var}: {'configured' if os.getenv(var) else 'missing'} - Value: {os.getenv(var, 'not set')[:10]}... (truncated for security)")
        else:
            logger.info(f"{var}: {'configured' if os.getenv(var) else 'missing'}")

    # Add CORS debug headers to help troubleshoot frontend issues
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

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

    logger.info("Registering direct client access routes - highest priority")
    
    # Unregister any existing rules for /api/auth/passcodes to avoid conflicts
    for rule in list(app.url_map.iter_rules()):
        if '/api/auth/passcodes' in rule.rule:
            app.url_map._rules.remove(rule)
            app.url_map._rules_by_endpoint.pop(rule.endpoint, None)
            logger.info(f"Removed conflicting rule: {rule.rule}")

    # Create direct endpoint at app level to bypass blueprint routing
    @app.route('/api/auth/passcodes', methods=['POST', 'GET', 'OPTIONS'])
    def direct_auth_passcodes():
        """Direct route for client access"""
        logger.info(f"Direct passcodes route hit: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Cookies: {request.cookies}")
        logger.info(f"Query params: {dict(request.args)}")
        
        # Handle OPTIONS for CORS preflight
        if request.method == 'OPTIONS':
            response = Response(
                status=204,
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
            return response
            
        # Import handler functions from auth_routes
        from .routes.auth_routes import get_passcodes, create_passcode
        
        try:
            if request.method == 'GET':
                return get_passcodes()
            elif request.method == 'POST':
                if not request.is_json and request.get_data():
                    # Try to parse JSON from raw data
                    try:
                        raw_data = request.get_data(as_text=True)
                        logger.info(f"Raw request data: {raw_data}")
                        data = json.loads(raw_data)
                        # Manually set the request JSON data
                        request._cached_json = (data, raw_data)
                        request.json = data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {str(e)}")
                        return jsonify({"message": f"Invalid JSON data: {str(e)}"}), 400
                    
                # Now process the request
                return create_passcode()
        except Exception as e:
            logger.error(f"Error in direct_auth_passcodes: {str(e)}")
            logger.exception("Detailed error:")
            return jsonify({"message": f"Server error: {str(e)}"}), 500

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
        # Register blueprints with better error handling
        def register_blueprints_with_error_handling(app):
            # Register auth blueprint but modify its URL prefix to avoid conflict
            try:
                from .routes.auth_routes import auth
                # Register with the original prefix to match frontend expectations
                app.register_blueprint(auth, url_prefix='/api')
                logger.info("Auth blueprint registered with original prefix to match frontend")
            except Exception as e:
                logger.error(f"Failed to register auth blueprint: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())

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

            try:
                from .routes.webhooks import webhooks as webhooks_blueprint
                app.register_blueprint(webhooks_blueprint, url_prefix='/api')
                logger.info("Webhooks blueprint registered successfully with prefix /api")
            except Exception as e:
                logger.error(f"Failed to register webhooks blueprint: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())

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
            logger.info(f"Endpoint: {rule.endpoint}, Path: {rule.rule}, Methods: {rule.methods}")
            
        # Add debug route to catch and log all requests
        @app.route('/api/auth/passcodes', methods=['GET', 'POST', 'OPTIONS'])
        def debug_passcodes():
            logger.info(f"Debug route hit: {request.method} {request.path}")
            logger.info(f"Headers: {dict(request.headers)}")
            logger.info(f"Cookies: {request.cookies}")
            
            # Direct handler implementation for production
            try:
                if request.method == 'GET':
                    # Handle GET request directly
                    business_id = request.args.get('business_id')
                    logger.info(f"Getting passcodes for business_id: {business_id}")
                    
                    if not business_id:
                        logger.warning("Business ID not provided")
                        return Response(
                            json.dumps({"message": "Business ID is required", "clients": []}),
                            status=200,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Verify admin auth from headers or cookies
                    auth_header = request.headers.get('Authorization', '')
                    admin_cookie = request.cookies.get('admin', '')
                    admin_token = None
                    
                    if auth_header and auth_header.startswith('Bearer '):
                        admin_token = auth_header.replace('Bearer ', '')
                    
                    is_admin = (admin_token == "97225" or admin_cookie == "97225")
                    logger.info(f"Admin authentication status: {is_admin}")
                    
                    if not is_admin:
                        logger.warning("Unauthorized access attempt")
                        return Response(
                            json.dumps({"message": "Unauthorized access"}),
                            status=401,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Get passcodes from database
                    try:
                        from app.models import ClientPasscode
                        passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
                        passcode_list = [p.to_dict() for p in passcodes]
                        logger.info(f"Found {len(passcode_list)} passcodes")
                        return Response(
                            json.dumps({"clients": passcode_list}),
                            status=200,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    except Exception as e:
                        logger.error(f"Database error: {str(e)}")
                        logger.exception("Detailed error:")
                        return Response(
                            json.dumps({"message": f"Database error: {str(e)}", "clients": []}),
                            status=200,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                        
                elif request.method == 'POST':
                    # Handle POST request directly
                    data = request.get_json()
                    logger.info(f"Creating passcode with data: {data}")
                    
                    # Verify admin auth
                    auth_header = request.headers.get('Authorization', '')
                    admin_cookie = request.cookies.get('admin', '')
                    admin_token = None
                    
                    if auth_header and auth_header.startswith('Bearer '):
                        admin_token = auth_header.replace('Bearer ', '')
                    
                    is_admin = (admin_token == "97225" or admin_cookie == "97225")
                    logger.info(f"Admin authentication status: {is_admin}")
                    
                    if not is_admin:
                        logger.warning("Unauthorized access attempt")
                        return Response(
                            json.dumps({"message": "Unauthorized access"}),
                            status=401,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    if not data:
                        logger.warning("No data provided")
                        return Response(
                            json.dumps({"message": "No data provided"}),
                            status=400,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                            
                    business_id = data.get('business_id')
                    passcode = data.get('passcode')
                    permissions = data.get('permissions')
                    
                    # Validation
                    if not business_id:
                        return Response(
                            json.dumps({"message": "Business ID is required"}),
                            status=400,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    if not passcode:
                        return Response(
                            json.dumps({"message": "Passcode is required"}),
                            status=400,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    if not permissions:
                        permissions = {}  # Default empty dict
                    
                    # Create passcode
                    from app.models import ClientPasscode, Business
                    
                    # Check if business exists
                    business = db.session.query(Business).filter_by(id=business_id).first()
                    if not business:
                        logger.warning(f"Business not found: {business_id}")
                        return Response(
                            json.dumps({"message": f"Business not found: {business_id}"}),
                            status=404,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Check if passcode exists
                    existing = db.session.query(ClientPasscode).filter_by(
                        business_id=business_id, passcode=passcode).first()
                    if existing:
                        return Response(
                            json.dumps({"message": "Passcode already exists"}),
                            status=409,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Ensure permissions is stored correctly
                    try:
                        if isinstance(permissions, dict):
                            permissions_json = json.dumps(permissions)
                        elif isinstance(permissions, list):
                            permissions_json = json.dumps(permissions)
                        elif isinstance(permissions, str):
                            # Make sure it's valid JSON
                            json.loads(permissions)  # This will raise an exception if invalid
                            permissions_json = permissions
                        else:
                            permissions_json = json.dumps({})
                    except Exception as e:
                        logger.error(f"Error processing permissions: {str(e)}")
                        permissions_json = json.dumps({})
                    
                    # For troubleshooting, log what's actually being stored
                    logger.info(f"Final permissions JSON: {permissions_json}")
                    
                    # Create new passcode
                    new_passcode = ClientPasscode(
                        business_id=business_id,
                        passcode=passcode,
                        permissions=permissions_json
                    )
                    db.session.add(new_passcode)
                    db.session.commit()
                    logger.info(f"Created new passcode with ID: {new_passcode.id}")
                    return Response(
                        json.dumps({"message": "Client access created successfully"}),
                        status=201,
                        mimetype='application/json',
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                        }
                    )
                except Exception as e:
                    if db and hasattr(db, 'session') and hasattr(db.session, 'rollback'):
                        db.session.rollback()
                    logger.error(f"Error creating passcode: {str(e)}")
                    logger.exception("Detailed error:")
                    return Response(
                        json.dumps({"message": f"Error creating client access: {str(e)}"}),
                        status=500,
                        mimetype='application/json',
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                        }
                    )
        except Exception as e:
            logger.error(f"Error in debug_passcodes: {str(e)}")
            logger.exception("Detailed error:")
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
    logger.info("Application creation completed successfully")
    return app

# Create the Flask application instance
app = create_app()
