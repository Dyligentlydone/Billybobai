from flask import Flask, jsonify, request
import logging
import sys
import traceback
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create application factory
def create_app():
    logger.info("Starting application creation from app.py...")
    app = Flask(__name__)
    
    # Configure CORS
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
         supports_credentials=True)
             
    # Add CORS headers to all responses
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response
        
    # Register blueprints with error handling
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/')
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "API is running",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    logger.info("Application creation completed successfully in app.py")
    return app

def register_blueprints(app):
    """Register all blueprints with the application"""
    logger.info("Registering blueprints from app.py")
    
    try:
        # Import and register analytics blueprint
        from routes.analytics import analytics_bp
        app.register_blueprint(analytics_bp)
        logger.info("Successfully registered analytics blueprint")
        
        # Import and register business routes blueprint
        try:
            from app.routes.business_routes import business_bp
            app.register_blueprint(business_bp)
            logger.info("Successfully registered business routes blueprint")
        except ImportError:
            logger.warning("Business routes not found, skipping")
        except Exception as e:
            logger.error(f"Error registering business routes blueprint: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        # Import and register conversation analytics blueprint
        try:
            from routes.conversation_analytics import conversation_bp
            app.register_blueprint(conversation_bp)
            logger.info("Successfully registered conversation analytics blueprint")
        except ImportError:
            logger.warning("Conversation analytics routes not found, skipping")
        except Exception as e:
            logger.error(f"Error registering conversation analytics blueprint: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# Initialize app (for gunicorn)
try:
    logger.info("Initializing application for gunicorn")
    app = create_app()
except Exception as e:
    logger.error(f"Error initializing application: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
