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
         resources={r"/*": {"origins": [
                 "http://localhost:3000",
                 "http://localhost:5173",
                 "http://localhost:4173",
                 "http://127.0.0.1:5173",
                 "https://billybobai-production-6713.up.railway.app",
                 "https://billybobai-production.up.railway.app",
                 "https://www.dyligent.xyz",
             ]}},
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
        from app.models.business import Business, BusinessConfig
        from app.models.email import EmailThread, InboundEmail
        from app.models.workflow import Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution
        from app.models.client_passcode import ClientPasscode
        from app.models.sms_consent import SMSConsent
        from app.models.sms_settings import SMSSettings
        from app.models.message import Message, MessageDirection, MessageChannel, MessageStatus
        # Add other models here if needed
        logger.info("All major models imported successfully for metadata registration")
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
    
    # Add app-level error handlers to catch 404s and return JSON instead of HTML
    @app.errorhandler(404)
    def handle_404(e):
        """Return JSON for 404 errors instead of HTML"""
        logger.warning(f"404 error: {request.path}")
        
        # Special case for auth/passcodes routes that are getting 404s
        if '/api/auth/passcodes' in request.path:
            logger.info(f"Intercepting 404 for passcodes route: {request.path}")
            # Check if this is a GET request with business_id and admin parameters
            if request.method == 'GET' and 'business_id' in request.args and 'admin' in request.args:
                logger.info(f"Redirecting to passcodes handler with args: {request.args}")
                from .routes.auth_routes import get_passcodes
                return get_passcodes()
            # Check if this is a POST request for creating passcodes
            elif request.method == 'POST' and request.is_json:
                logger.info(f"Redirecting to passcode creation handler")
                from .routes.auth_routes import create_passcode
                return create_passcode()
                
        return jsonify({"error": "Not found", "message": "The requested resource was not found"}), 404
    
    # Add a before_request handler to intercept ALL passcodes requests at the app level
    @app.before_request
    def handle_passcodes_requests():
        """Intercept any passcodes requests at the app level"""
        if '/api/auth/passcodes' in request.path:
            logger.info(f"Intercepting passcodes request: {request.method} {request.path}")
            logger.info(f"Query params: {request.args}")
            
            # Add CORS headers for cross-origin requests
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
            
            # Handle OPTIONS pre-flight requests
            if request.method == 'OPTIONS':
                return ('', 204, headers)
            
            try:
                from .routes.auth_routes import get_passcodes, create_passcode
                
                if request.method == 'GET':
                    # Log incoming GET request for client access
                    logger.info(f"GET passcodes: business_id={request.args.get('business_id')}, admin token provided: {'admin' in request.args}")
                    return get_passcodes()
                elif request.method == 'POST':
                    # Log incoming POST request for client access
                    logger.info(f"CREATE passcode: {request.get_json() if request.is_json else 'No JSON data'}")
                    return create_passcode()
            except Exception as e:
                logger.error(f"Error in handle_passcodes_requests: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({"error": str(e)}), 500
        return None

    @app.before_request
    def handle_direct_clients_requests():
        """Intercept any direct-clients requests at the app level"""
        if '/api/auth/direct-clients' in request.path:
            logger.info(f"Intercepting direct-clients request: {request.method} {request.path}")
            
            # Handle OPTIONS pre-flight requests
            if request.method == 'OPTIONS':
                response = jsonify({})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                return response, 204
                
            try:
                from .routes.auth_routes import direct_clients
                return direct_clients()
            except Exception as e:
                logger.error(f"Error handling direct-clients: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({"clients": [], "error": str(e)}), 200
                
        return None
        
    # Also register direct routes at the app level to ensure they're accessible
    @app.route('/api/auth/direct-clients', methods=['GET', 'POST', 'OPTIONS'])
    def app_direct_clients():
        """App-level direct route for client access that bypasses any blueprint registration issues"""
        logger.info(f"App-level direct-clients route hit: {request.method} {request.path}")
        # Import the function from auth_routes to handle the request
        try:
            from .routes.auth_routes import direct_clients
            return direct_clients()
        except Exception as e:
            logger.error(f"Error in app_direct_clients: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e), "clients": []}), 200
        
    @app.route('/api/auth/direct-client-create', methods=['POST', 'OPTIONS'])
    def app_direct_client_create():
        """App-level direct route for client access creation"""
        logger.info(f"App-level direct-client-create route hit: {request.method} {request.path}")
        from .routes.auth_routes import direct_client_create
        return direct_client_create()

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
        # Register auth blueprint with the correct prefix that matches frontend expectations
        from .routes.auth_routes import auth
        # Register WITHOUT additional prefix to avoid double-prefixing
        app.register_blueprint(auth)
        logger.info("Auth blueprint registered with its own prefix /api to match frontend expectations")
    except Exception as e:
        logger.error(f"Failed to register auth blueprint: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    try:
        # Register blueprints with better error handling
        def register_blueprints_with_error_handling(app):
            try:
                # Only attempt to import calendly routes if the module exists
                try:
                    from .routes import calendly_routes
                    app.register_blueprint(calendly_routes.calendly_bp)
                    logger.info("Calendly blueprint registered successfully")
                except ImportError:
                    logger.warning("Calendly routes not found, skipping")
                except Exception as e:
                    logger.error(f"Error registering Calendly blueprint: {str(e)}")

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

                try:
                    from .routes.client_routes import clients_bp
                    app.register_blueprint(clients_bp)  # prefix already defined in blueprint
                    logger.info("Clients blueprint registered successfully")
                except Exception as e:
                    logger.error(f"Failed to register clients blueprint: {str(e)}")

                # Add other blueprints here as needed
            except Exception as e:
                logger.error(f"Error in register_blueprints: {str(e)}")

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

        # === DEBUG: Print all registered routes at startup ===
        logger.info("=== Registered Flask Routes ===")
        for rule in app.url_map.iter_rules():
            logger.info(f"ROUTE: {rule} -> methods: {sorted(rule.methods)}")
        logger.info("=== END ROUTE LIST ===")

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
            logger.info(f"Data: {request.get_json() if request.is_json else 'None'}")
            logger.info(f"Args: {request.args}")
            
            # Direct handler implementation for production
            try:
                if request.method == 'GET':
                    # Handle GET request directly
                    business_id = request.args.get('business_id')
                    logger.info(f"Getting passcodes for business_id: {business_id}")
                    
                    if not business_id:
                        logger.warning("Business ID not provided")
                        return jsonify({"message": "Business ID is required", "clients": []}), 200
                    
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
                        return jsonify({"message": "Unauthorized access"}), 200
                    
                    # Get passcodes from database
                    try:
                        from app.models import ClientPasscode
                        passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
                        passcode_list = [p.to_dict() for p in passcodes]
                        logger.info(f"Found {len(passcode_list)} passcodes")
                        return jsonify({"clients": passcode_list}), 200
                    except Exception as e:
                        logger.error(f"Database error: {str(e)}")
                        logger.exception("Detailed error:")
                        return jsonify({"message": "Database error", "clients": []}), 200
                        
                elif request.method == 'POST':
                    # Handle POST request directly
                    data = request.get_json()
                    logger.info(f"POST request with data: {data}")
                    
                    # -----------------------------------------------------------
                    # CLIENT PASSCODE VERIFICATION - No admin auth needed
                    # -----------------------------------------------------------
                    # If payload contains just a passcode for verification,
                    # bypass all other checks since this is from a client login
                    # -----------------------------------------------------------
                    if data and isinstance(data, dict) and 'passcode' in data and len(data) == 1:
                        passcode_value = data.get('passcode')
                        logger.info(f"Passcode verification request for code: {passcode_value}")
                        
                        try:
                            from app.models import ClientPasscode
                            matching = db.session.query(ClientPasscode).filter_by(passcode=passcode_value).all()
                            clients_list = [p.to_dict() for p in matching]
                            logger.info(f"Verification found {len(clients_list)} matching passcodes")
                            return jsonify({"message": "Success", "clients": clients_list}), 200
                        except Exception as e:
                            logger.error(f"Database error during passcode verification: {str(e)}")
                            logger.exception("Detailed error:")
                            return jsonify({"message": "Error verifying passcode", "clients": [], "error": str(e)}), 500
                    
                    # For anything else, this is the admin passcode creation flow
                    # Verify admin auth from headers
                    auth_header = request.headers.get('Authorization', '')
                    admin_cookie = request.cookies.get('admin', '')
                    admin_token = None
                    
                    if auth_header and auth_header.startswith('Bearer '):
                        admin_token = auth_header.replace('Bearer ', '')
                    
                    is_admin = (admin_token == "97225" or admin_cookie == "97225")
                    logger.info(f"Admin authentication status: {is_admin}")
                    
                    if not is_admin:
                        logger.warning("Unauthorized access attempt")
                        return jsonify({"message": "Unauthorized access"}), 200
                    
                    if not data:
                        logger.warning("No data provided")
                        return jsonify({"message": "No data provided"}), 200

                    # Otherwise, treat it as a create passcode request
                    business_id = data.get('business_id')
                    passcode = data.get('passcode')
                    permissions = data.get('permissions')
                    
                    # Validation
                    if not business_id:
                        return jsonify({"message": "Business ID is required"}), 200
                    
                    if not passcode:
                        return jsonify({"message": "Passcode is required"}), 200
                    
                    # Special handling for 'admin' as business_id
                    if business_id == 'admin':
                        return jsonify({"message": "Invalid business ID"}), 200
                    
                    # Check if business exists
                    from app.models import Business
                    business = db.session.query(Business).filter_by(id=business_id).first()
                    if not business:
                        return jsonify({"message": "Business not found"}), 200
                    
                    # Process permissions
                    import json
                    if isinstance(permissions, dict):
                        permissions_json = json.dumps(permissions)
                    elif isinstance(permissions, str):
                        # Validate JSON
                        json.loads(permissions)
                        permissions_json = permissions
                    else:
                        return jsonify({"message": "Invalid permissions format"}), 200
                    
                    # Check if passcode exists
                    from app.models import ClientPasscode
                    existing = db.session.query(ClientPasscode).filter_by(
                        business_id=business_id, passcode=passcode).first()
                    if existing:
                        return jsonify({"message": "Passcode already exists"}), 200
                    
                    # Create new passcode
                    try:
                        new_passcode = ClientPasscode(
                            business_id=business_id,
                            passcode=passcode,
                            permissions=permissions_json
                        )
                        db.session.add(new_passcode)
                        db.session.commit()
                        logger.info(f"Created new passcode with ID: {new_passcode.id}")
                        return jsonify({"message": "Client access created successfully"}), 200
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error creating passcode: {str(e)}")
                        logger.exception("Detailed error:")
                        return jsonify({"message": f"Error creating client access: {str(e)}"}), 200
                
                # OPTIONS request
                return '', 204
                
            except Exception as e:
                logger.error(f"Error in debug_passcodes: {str(e)}")
                logger.exception("Detailed error:")
                return jsonify({"error": str(e)}), 200
                
        logger.info("Application creation completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        # Log the full traceback for debugging
        import traceback
        logger.error(traceback.format_exc())
        
    # Tell Flask to use application root for all URLs
    app.config['APPLICATION_ROOT'] = '/'

    @app.route('/')
    def health_check():
        """Health check endpoint for Railway."""
        # Simple health check - no logic, just return success
        return jsonify({
            "status": "healthy",
            "message": "API is running",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    @app.route('/health')
    def health_check_endpoint():
        """Health check endpoint for Railway."""
        # Simple health check - no logic, just return success
        return jsonify({
            "status": "healthy",
            "message": "API is running",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    # Add a dedicated route for client access operations that won't interfere with health checks
    @app.route('/api/client-operations', methods=['GET', 'POST'])
    def client_operations():
        """Dedicated endpoint for client access operations."""
        logger.info(f"Client operations route hit: {request.method} {request.path}")
        
        try:
            # Handle GET requests for fetching clients
            if request.method == 'GET':
                # Extract parameters
                business_id = request.args.get('business_id', '')
                admin_token = request.args.get('admin', '')
                
                logger.info(f"Fetching clients for business_id: {business_id}")
                
                # Check admin authentication
                is_admin = (admin_token == "97225")
                
                if not is_admin:
                    logger.warning("Unauthorized access attempt")
                    return jsonify({"clients": [], "message": "Unauthorized"}), 200
                
                # Handle special cases
                if not business_id or business_id == 'admin':
                    return jsonify({"clients": []}), 200
                
                # Check if business exists and fetch clients
                try:
                    from .models import ClientPasscode, Business
                    # Verify business exists
                    business = db.session.query(Business).filter_by(id=business_id).first()
                    if not business:
                        logger.warning(f"Business not found: {business_id}")
                        return jsonify({"clients": []}), 200
                        
                    # Get passcodes
                    passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
                    passcode_list = [passcode.to_dict() for passcode in passcodes]
                    
                    return jsonify({"clients": passcode_list}), 200
                except Exception as e:
                    logger.error(f"Error fetching clients: {str(e)}")
                    return jsonify({"clients": [], "error": str(e)}), 200
                
            # Handle POST requests for creating clients
            elif request.method == 'POST':
                admin_token = request.args.get('admin', '')
                
                # Check admin authentication
                is_admin = (admin_token == "97225")
                
                if not is_admin:
                    logger.warning("Unauthorized access attempt")
                    return jsonify({"message": "Unauthorized"}), 200
                
                # Process the request body
                if not request.is_json:
                    logger.warning("Request is not JSON")
                    return jsonify({"message": "Invalid request format"}), 200
                    
                data = request.get_json()
                business_id = data.get('business_id')
                passcode = data.get('passcode')
                permissions = data.get('permissions')
                
                # Validate required fields
                if not business_id:
                    return jsonify({"message": "Business ID is required"}), 200
                    
                if not passcode:
                    return jsonify({"message": "Passcode is required"}), 200
                
                # Check if business exists
                from .models import Business, ClientPasscode
                business = db.session.query(Business).filter_by(id=business_id).first()
                if not business:
                    return jsonify({"message": "Business not found"}), 200
                    
                # Check if passcode exists
                existing = db.session.query(ClientPasscode).filter_by(
                    business_id=business_id, passcode=passcode).first()
                if existing:
                    return jsonify({"message": "Passcode already exists"}), 200
                    
                # Create new passcode
                try:
                    import json
                    # Format permissions
                    if isinstance(permissions, dict):
                        permissions_json = json.dumps(permissions)
                    elif isinstance(permissions, str):
                        json.loads(permissions)  # Validate JSON format
                        permissions_json = permissions
                    else:
                        permissions_json = json.dumps({})
                        
                    # Create and save new passcode
                    new_passcode = ClientPasscode(
                        business_id=business_id,
                        passcode=passcode,
                        permissions=permissions_json
                    )
                    db.session.add(new_passcode)
                    db.session.commit()
                    
                    logger.info(f"Created new passcode for business: {business_id}")
                    return jsonify({"message": "Client access created successfully"}), 200
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error creating passcode: {str(e)}")
                    return jsonify({"message": f"Error creating client access: {str(e)}"}), 200
            
        except Exception as e:
            logger.error(f"Error in client_operations: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 200

    # Add a unified client bridge endpoint to ensure compatibility
    @app.route('/api/client-bridge', methods=['GET', 'POST', 'OPTIONS'])
    def client_bridge():
        """
        A simple API bridge that serves as a unified endpoint for client operations
        to avoid routing issues in Railway. This endpoint will determine the operation
        based on the request body.
        """
        logger.info(f"Client bridge hit: {request.method} {request.path} with args: {request.args}")
        
        try:
            # Handle OPTIONS pre-flight requests
            if request.method == 'OPTIONS':
                response = jsonify({})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                return response, 204
                
            # Check for admin token in query param, header, or cookie
            admin_token = request.args.get('admin', '')
            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.startswith('Bearer '):
                auth_header = auth_header[7:]  # Remove 'Bearer ' prefix
                
            # Validate admin token
            is_admin = (admin_token == "97225" or auth_header == "97225")
            
            if not is_admin:
                logger.warning("Unauthorized access attempt to client bridge")
                return jsonify({"message": "Unauthorized"}), 200
                
            # Handle GET requests
            if request.method == 'GET':
                # Extract business_id
                business_id = request.args.get('business_id', '')
                operation = request.args.get('operation', 'fetch_clients')
                
                logger.info(f"Bridge GET: Operation={operation}, business_id={business_id}")
                
                # Default to fetch_clients operation for GET requests
                if operation == 'fetch_clients' or not operation:
                    logger.info(f"Bridge: Fetching clients for business_id: {business_id}")
                    
                    if not business_id:
                        # When no business_id is provided, get it from the authenticated user
                        from .models import Business
                        # Get first business as a fallback
                        business = db.session.query(Business).first()
                        if business:
                            business_id = business.id
                            logger.info(f"Using default business ID: {business_id}")
                    
                    if not business_id or business_id == 'admin':
                        # Return empty list for admin or missing business ID
                        return jsonify({"clients": []}), 200
                            
                    # Get clients for the business
                    from .models import ClientPasscode
                    passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
                    passcode_list = [passcode.to_dict() for passcode in passcodes]
                    
                    logger.info(f"Returning {len(passcode_list)} clients")
                    return jsonify({"clients": passcode_list}), 200
                    
                # Unknown operation
                return jsonify({"message": f"Unknown operation: {operation}"}), 200
                
            # Handle POST requests
            elif request.method == 'POST':
                # Parse operation from request
                if not request.is_json:
                    return jsonify({"message": "Invalid request format"}), 200
                    
                data = request.get_json()
                operation = data.get('operation', 'create_client')
                
                if operation == 'create_client':
                    # Process data for client creation
                    business_id = data.get('business_id', '')
                    passcode = data.get('passcode', '')
                    permissions = data.get('permissions', {})
                    
                    logger.info(f"Bridge: Creating client for business_id: {business_id}, passcode: {passcode}")
                    
                    # Validate required fields
                    if not business_id:
                        return jsonify({"message": "Business ID is required"}), 200
                            
                    if not passcode:
                        return jsonify({"message": "Passcode is required"}), 200
                            
                    # Special handling for 'admin' as business_id
                    if business_id == 'admin':
                        return jsonify({"message": "Invalid business ID"}), 200
                            
                    # Check if business exists
                    from .models import Business
                    business = db.session.query(Business).filter_by(id=business_id).first()
                    if not business:
                        return jsonify({"message": "Business not found"}), 200
                            
                    # Process permissions
                    import json
                    if isinstance(permissions, dict):
                        permissions_json = json.dumps(permissions)
                    elif isinstance(permissions, str):
                        # Validate JSON
                        json.loads(permissions)
                        permissions_json = permissions
                    else:
                        return jsonify({"message": "Invalid permissions format"}), 200
                            
                    # Check if passcode exists
                    from .models import ClientPasscode
                    existing = db.session.query(ClientPasscode).filter_by(
                        business_id=business_id, passcode=passcode).first()
                    if existing:
                        return jsonify({"message": "Passcode already exists"}), 200
                            
                    # Create new passcode
                    try:
                        new_passcode = ClientPasscode(
                            business_id=business_id,
                            passcode=passcode,
                            permissions=permissions_json
                        )
                        db.session.add(new_passcode)
                        db.session.commit()
                        logger.info(f"Created new passcode: {passcode}")
                        return jsonify({"message": "Client access created successfully"}), 200
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error creating passcode: {str(e)}")
                        return jsonify({"message": f"Error creating client access: {str(e)}"}), 200
                else:
                    logger.warning(f"Unknown operation: {operation}")
                    return jsonify({"message": f"Unknown operation: {operation}"}), 200
                        
        except Exception as e:
            logger.error(f"Error in client_bridge: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"message": f"Error: {str(e)}"}), 200
            
    # Add a fully standalone direct-clients endpoint that doesn't depend on importing from auth_routes.py
    @app.route('/api/auth/direct-clients', methods=['GET', 'POST', 'OPTIONS'])
    def standalone_direct_clients():
        """Standalone implementation of the direct-clients endpoint to bypass all import issues"""
        logger.info(f"Standalone direct-clients route hit: {request.method} {request.path}")
        logger.info(f"Query params: {request.args}")
        
        # Handle OPTIONS pre-flight requests
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response, 204
        
        try:
            # Check admin authentication from different sources
            admin_password = request.cookies.get('admin_password')
            auth_header = request.headers.get('Authorization')
            admin_token = request.args.get('admin')  # Get from query params for GET requests
            
            # For POST requests, get from request body
            if request.method == 'POST' and request.is_json:
                data = request.get_json() or {}
                if not admin_token:
                    admin_token = data.get('admin_token')
                business_id = data.get('business_id')
            else:
                # For GET requests, get from query params
                business_id = request.args.get('business_id')
            
            logger.info(f"Standalone: Processing for business_id: {business_id}, admin token: {admin_token}")
            
            # Check admin authentication
            is_admin = (admin_password == "97225" or 
                       (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                       admin_token == "97225")
            
            if not is_admin:
                logger.warning("Unauthorized access attempt")
                return jsonify({"message": "Unauthorized", "clients": []}), 200
                
            if not business_id:
                logger.warning("Business ID not provided")
                return jsonify({"message": "Business ID is required", "clients": []}), 200
            
            # Special handling for 'admin' as business_id
            if business_id == 'admin':
                logger.info("Admin business_id - returning empty client list")
                return jsonify({"message": "Success", "clients": []}), 200
                
            # Check if business exists - load models directly
            from app.models import Business, ClientPasscode
            from app.db import db
            
            business = db.session.query(Business).filter_by(id=business_id).first()
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return jsonify({"message": "Success", "clients": []}), 200
                    
            # Query passcodes for the business
            passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
            
            # Convert to dictionary for JSON response
            passcode_list = []
            for passcode in passcodes:
                try:
                    passcode_list.append(passcode.to_dict())
                except Exception as e:
                    logger.error(f"Error converting passcode to dict: {str(e)}")
            
            logger.info(f"Returning {len(passcode_list)} clients")
            return jsonify({"clients": passcode_list}), 200
            
        except Exception as e:
            logger.error(f"Error in standalone_direct_clients: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"message": "Error fetching clients", "clients": []}), 200

    # Add multiple root-level direct-clients endpoints with various path options to ensure one will work regardless of proxy configuration
    @app.route('/api/auth/direct-clients', methods=['GET', 'POST', 'OPTIONS'])
    @app.route('/auth/direct-clients', methods=['GET', 'POST', 'OPTIONS'])  # Try alternate path
    @app.route('/direct-clients', methods=['GET', 'POST', 'OPTIONS'])  # Try simplest path
    def root_direct_clients():
        """Root-level implementation of the direct-clients endpoint to bypass all routing issues"""
        logger.info(f"ROOT direct-clients route hit: {request.method} {request.path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Query params: {request.args}")
        logger.info(f"Request full URL: {request.url}")
        
        # Log more details about the request
        logger.info(f"Request blueprint: {request.blueprint}")
        logger.info(f"Request endpoint: {request.endpoint}")
        
        # Handle OPTIONS pre-flight requests
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response, 204
        
        try:
            # Check admin authentication from different sources
            admin_password = request.cookies.get('admin_password')
            auth_header = request.headers.get('Authorization')
            admin_token = request.args.get('admin')  # Get from query params for GET requests
            
            # For POST requests, get from request body
            if request.method == 'POST' and request.is_json:
                data = request.get_json() or {}
                if not admin_token:
                    admin_token = data.get('admin_token')
                business_id = data.get('business_id')
            else:
                # For GET requests, get from query params
                business_id = request.args.get('business_id')
            
            logger.info(f"ROOT: Processing for business_id: {business_id}, admin token present: {admin_token is not None}")
            
            # Check admin authentication
            is_admin = (admin_password == "97225" or 
                       (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                       admin_token == "97225")
            
            if not is_admin:
                logger.warning("Unauthorized access attempt")
                return jsonify({"message": "Unauthorized", "clients": []}), 200  # Return 200 instead of 401
                
            if not business_id:
                logger.warning("Business ID not provided")
                return jsonify({"message": "Business ID is required", "clients": []}), 200  # Return 200 instead of 400
            
            # Special handling for 'admin' as business_id
            if business_id == 'admin':
                logger.info("Admin business_id - returning empty client list")
                return jsonify({"message": "Success", "clients": []}), 200
                
            # Check if business exists - load models directly
            from app.models import Business, ClientPasscode
            from app.db import db
            
            business = db.session.query(Business).filter_by(id=business_id).first()
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return jsonify({"message": "Success", "clients": []}), 200
                    
            # Query passcodes for the business
            passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
            
            # Convert to dictionary for JSON response
            passcode_list = []
            for passcode in passcodes:
                try:
                    passcode_list.append(passcode.to_dict())
                except Exception as e:
                    logger.error(f"Error converting passcode to dict: {str(e)}")
            
            logger.info(f"Returning {len(passcode_list)} clients")
            return jsonify({"clients": passcode_list}), 200
            
        except Exception as e:
            logger.error(f"Error in root_direct_clients: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"message": "Error fetching clients", "clients": [], "error": str(e)}), 200

    # Add a clear catch-all route that will handle ANY path to direct-clients
    # This is a last resort to bypass Railway's routing issues
    @app.route('/<path:subpath>', methods=['GET', 'POST', 'OPTIONS'])
    def catch_all_direct_clients(subpath):
        """Catch all route to intercept any request to direct-clients regardless of path"""
        logger.info(f"CATCH-ALL received request: {request.method} {request.path}")
        logger.info(f"Subpath: {subpath}")
        
        # If this is the direct-clients route under any path
        if 'direct-clients' in subpath:
            logger.info(f"CATCH-ALL: Detected direct-clients request in {subpath}")
            
            # Handle OPTIONS pre-flight requests
            if request.method == 'OPTIONS':
                response = jsonify({})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                return response, 204
            
            try:
                # Extract admin token and business_id from any possible source
                admin_token = None
                business_id = None
                
                # Check query params (GET)
                if request.args:
                    admin_token = request.args.get('admin')
                    business_id = request.args.get('business_id')
                    logger.info(f"Found in query params: admin={admin_token}, business_id={business_id}")
                
                # Check request body (POST)
                if request.is_json and not (admin_token and business_id):
                    data = request.get_json() or {}
                    if not admin_token:
                        admin_token = data.get('admin_token')
                    if not business_id:
                        business_id = data.get('business_id')
                    logger.info(f"Found in JSON body: admin={admin_token}, business_id={business_id}")
                
                # Check form data (POST)
                if request.form and not (admin_token and business_id):
                    if not admin_token:
                        admin_token = request.form.get('admin_token')
                    if not business_id:
                        business_id = request.form.get('business_id')
                    logger.info(f"Found in form data: admin={admin_token}, business_id={business_id}")
                
                # Check headers
                auth_header = request.headers.get('Authorization')
                if auth_header:
                    logger.info(f"Found Authorization header: {auth_header}")
                
                # Check cookies
                admin_password = request.cookies.get('admin_password')
                if admin_password:
                    logger.info(f"Found admin_password cookie")
                
                # Log full details
                logger.info(f"CATCH-ALL Client request details:")
                logger.info(f"  - Headers: {dict(request.headers)}")
                logger.info(f"  - Args: {dict(request.args)}")
                logger.info(f"  - Form: {dict(request.form) if request.form else 'None'}")
                logger.info(f"  - JSON: {request.get_json() if request.is_json else 'None'}")
                logger.info(f"  - Cookies: {request.cookies}")
                
                # Admin authentication
                is_admin = (admin_password == "97225" or 
                           (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                           admin_token == "97225")
                
                if not is_admin:
                    logger.warning("CATCH-ALL: Unauthorized access attempt")
                    return jsonify({"message": "Unauthorized", "clients": []}), 200
                    
                if not business_id:
                    logger.warning("CATCH-ALL: Business ID not provided")
                    return jsonify({"message": "Business ID is required", "clients": []}), 200
                
                # Special handling for 'admin' as business_id
                if business_id == 'admin':
                    logger.info("CATCH-ALL: Admin business_id - returning empty client list")
                    return jsonify({"message": "Success", "clients": []}), 200
                    
                # Check if business exists - load models directly
                from app.models import Business, ClientPasscode
                from app.db import db
                
                business = db.session.query(Business).filter_by(id=business_id).first()
                if not business:
                    logger.warning(f"CATCH-ALL: Business not found: {business_id}")
                    return jsonify({"message": "Success", "clients": []}), 200
                        
                # Query passcodes for the business
                passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
                
                # Convert to dictionary for JSON response
                passcode_list = []
                for passcode in passcodes:
                    try:
                        passcode_list.append(passcode.to_dict())
                    except Exception as e:
                        logger.error(f"CATCH-ALL: Error converting passcode to dict: {str(e)}")
                
                logger.info(f"CATCH-ALL: Returning {len(passcode_list)} clients")
                return jsonify({"clients": passcode_list}), 200
                
            except Exception as e:
                logger.error(f"CATCH-ALL: Error processing direct-clients: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({"message": "Error fetching clients", "clients": [], "error": str(e)}), 200
        
        # For all other paths
        return jsonify({"message": "Path not found", "path": subpath}), 200

    logger.info("Application creation completed successfully")
    return app

# Create the Flask application instance
app = create_app()
