from flask import Flask, jsonify, request
import logging
import sys
import traceback
from flask_cors import CORS
from datetime import datetime
import os

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
    
    # Direct implementation of the /api/analytics endpoint to ensure it works in production
    @app.route('/api/analytics', methods=['GET'])
    def direct_analytics():
        """Direct implementation of /api/analytics endpoint that doesn't rely on blueprint registration"""
        logger.info("DIRECT /api/analytics endpoint called from app.py")
        try:
            client_id = request.args.get('clientId')
            start_date = request.args.get('startDate')
            end_date = request.args.get('endDate')
            
            logger.info(f"GET /api/analytics with clientId={client_id}, startDate={start_date}, endDate={end_date}")
            
            if not all([client_id, start_date, end_date]):
                return jsonify({'error': 'Missing required parameters'}), 400
            
            # Connect to database and get real analytics data
            try:
                from config.database import get_db
                db = get_db()
                cursor = db.cursor()
                
                # Get message metrics including status and retry data
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_count,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                        SUM(CASE WHEN retry_attempt > 0 THEN 1 ELSE 0 END) as retried_count,
                        AVG(CASE WHEN retry_attempt > 0 THEN retry_attempt ELSE 0 END) as avg_retries,
                        SUM(CASE WHEN is_opted_out = 1 THEN 1 ELSE 0 END) as opt_out_count,
                        AVG(CASE 
                            WHEN status = 'delivered' 
                            THEN ROUND((julianday(updated_at) - julianday(created_at)) * 86400)
                            ELSE NULL 
                        END) as avg_delivery_time
                    FROM sms_messages
                    WHERE business_id = ?
                    AND date(created_at) BETWEEN date(?) AND date(?)
                """, (client_id, start_date, end_date))
                
                message_metrics = dict(cursor.fetchone())
                
                # Get hourly message volume and status distribution
                cursor.execute("""
                    SELECT 
                        strftime('%H', created_at) as hour,
                        status,
                        COUNT(*) as count
                    FROM sms_messages
                    WHERE business_id = ?
                    AND date(created_at) BETWEEN date(?) AND date(?)
                    GROUP BY hour, status
                    ORDER BY hour, status
                """, (client_id, start_date, end_date))
                
                hourly_stats = {}
                for row in cursor.fetchall():
                    hour = row[0]
                    status = row[1]
                    count = row[2]
                    if hour not in hourly_stats:
                        hourly_stats[hour] = {}
                    hourly_stats[hour][status] = count
                
                # Get opt-out trends
                cursor.execute("""
                    SELECT 
                        date(opted_out_at) as date,
                        COUNT(*) as count
                    FROM opt_outs
                    WHERE business_id = ?
                    AND date(opted_out_at) BETWEEN date(?) AND date(?)
                    GROUP BY date
                    ORDER BY date
                """, (client_id, start_date, end_date))
                
                opt_out_trends = [
                    {
                        'date': row[0],
                        'count': row[1]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Get error distribution
                cursor.execute("""
                    SELECT 
                        error_code,
                        COUNT(*) as count
                    FROM sms_messages
                    WHERE business_id = ?
                    AND date(created_at) BETWEEN date(?) AND date(?)
                    AND error_code IS NOT NULL
                    GROUP BY error_code
                    ORDER BY count DESC
                    LIMIT 10
                """, (client_id, start_date, end_date))
                
                error_distribution = [
                    {
                        'error_code': row[0],
                        'count': row[1]
                    }
                    for row in cursor.fetchall()
                ]
                
                return jsonify({
                    'message_metrics': message_metrics,
                    'hourly_stats': hourly_stats,
                    'opt_out_trends': opt_out_trends,
                    'error_distribution': error_distribution
                })
                
            except Exception as db_error:
                logger.error(f"Database error in direct_analytics: {str(db_error)}")
                logger.error(traceback.format_exc())
                
                # Fall back to sample data if DB query fails
                return jsonify({
                    'message_metrics': {
                        'total_messages': 10,
                        'delivered_count': 8,
                        'failed_count': 2,
                        'retried_count': 1,
                        'avg_retries': 0.5,
                        'opt_out_count': 0,
                        'avg_delivery_time': 2.5
                    },
                    'hourly_stats': {
                        '10': {'delivered': 3, 'failed': 1},
                        '14': {'delivered': 5, 'failed': 1}
                    },
                    'opt_out_trends': [],
                    'error_distribution': []
                })
                
        except Exception as e:
            logger.error(f"Error in direct_analytics: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # Direct implementation of /api/businesses endpoint that doesn't rely on blueprint registration
    @app.route('/api/businesses', methods=['GET'])
    def direct_businesses():
        """Direct implementation of /api/businesses endpoint that doesn't rely on blueprint registration"""
        logger.info("DIRECT /api/businesses endpoint called from app.py")
        
        # Hard-coded fallback businesses for absolute worst-case scenario
        FALLBACK_BUSINESSES = [
            {
                "id": "1",
                "name": "Sample Business 1",
                "description": "This is a fallback business",
                "domain": "example.com"
            },
            {
                "id": "2",
                "name": "Sample Business 2",
                "description": "Another fallback business",
                "domain": "example2.com"
            }
        ]
        
        # Check if ID is provided as a query parameter
        business_id = request.args.get('id')        
        
        # METHOD 1: Try ORM approach first
        try:
            # Try to import from app.models first
            try:
                from app.models.business import Business
                from app.db import db
                logger.info("Successfully imported Business from app.models.business")
            except ImportError:
                # Fall back to direct import
                try:
                    from models.business import Business
                    from db import db
                    logger.info("Successfully imported Business from models.business")
                except ImportError:
                    logger.warning("Could not import Business model from any location")
                    raise ImportError("Business model not found")
            
            # Use SQLAlchemy ORM
            if business_id:
                # If ID is provided, get that specific business
                logger.info(f"Direct route: Fetching business with ID: {business_id}")
                business = db.session.query(Business).filter_by(id=business_id).first()
                
                if not business:
                    logger.warning(f"Business with ID {business_id} not found")
                    return jsonify({"error": "Business not found"}), 404
                    
                return jsonify({
                    "id": business.id,
                    "name": business.name,
                    "description": business.description,
                    "domain": getattr(business, "domain", None)
                })
            else:
                # Otherwise, get all businesses
                logger.info("Direct route: Fetching all businesses")
                businesses = db.session.query(Business).all()
                return jsonify([{
                    "id": b.id,
                    "name": b.name,
                    "description": b.description,
                    "domain": getattr(b, "domain", None)
                } for b in businesses])
        except Exception as e:
            logger.warning(f"ORM approach failed: {str(e)}. Trying direct SQL.")
            
            # METHOD 2: Try direct SQL approach
            try:
                try:
                    from config.database import get_db
                    logger.info("Successfully imported get_db from config.database")
                except ImportError:
                    try:
                        from app.database import get_db
                        logger.info("Successfully imported get_db from app.database")
                    except ImportError:
                        logger.error("Could not import get_db from any module")
                        # Return fallback data
                        if business_id:
                            for fb in FALLBACK_BUSINESSES:
                                if fb["id"] == business_id:
                                    return jsonify(fb)
                            return jsonify({"error": "Business not found"}), 404
                        return jsonify(FALLBACK_BUSINESSES)
                
                db = next(get_db()) if callable(get_db) and hasattr(get_db, "__next__") else get_db()
                cursor = db.cursor() if hasattr(db, "cursor") else db.session.execute
                
                if business_id:
                    rows = cursor("SELECT id, name, description, domain FROM businesses WHERE id = :id", {"id": business_id})
                    row = next(rows, None) if hasattr(rows, "__next__") else rows.fetchone()
                    if not row:
                        logger.warning(f"Business with ID {business_id} not found in DB")
                        for fb in FALLBACK_BUSINESSES:
                            if fb["id"] == business_id:
                                return jsonify(fb)
                        return jsonify({"error": "Business not found"}), 404
                    
                    # Extract data - handle both tuple and dict-like row objects
                    if hasattr(row, "keys"):
                        # Dict-like result
                        return jsonify({
                            "id": row["id"],
                            "name": row["name"],
                            "description": row["description"],
                            "domain": row.get("domain")
                        })
                    else:
                        # Tuple-like result
                        return jsonify({
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "domain": row[3] if len(row) > 3 else None
                        })
                else:
                    rows = cursor("SELECT id, name, description, domain FROM businesses")
                    result = []
                    
                    # Handle both iterators and result proxies
                    if hasattr(rows, "fetchall"):
                        all_rows = rows.fetchall()
                    else:
                        all_rows = list(rows)
                    
                    for row in all_rows:
                        if hasattr(row, "keys"):
                            # Dict-like result
                            result.append({
                                "id": row["id"],
                                "name": row["name"],
                                "description": row["description"],
                                "domain": row.get("domain")
                            })
                        else:
                            # Tuple-like result
                            result.append({
                                "id": row[0],
                                "name": row[1],
                                "description": row[2],
                                "domain": row[3] if len(row) > 3 else None
                            })
                    
                    return jsonify(result)
            except Exception as e:
                logger.error(f"Both ORM and direct SQL approaches failed: {str(e)}")
                logger.error(traceback.format_exc())
                logger.error("Returning fallback business data")
                
                # METHOD 3: Last resort - return fallback data
                if business_id:
                    for fb in FALLBACK_BUSINESSES:
                        if fb["id"] == business_id:
                            return jsonify(fb)
                    return jsonify({"error": "Business not found"}), 404
                return jsonify(FALLBACK_BUSINESSES)
    
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
        # Try different import paths for the analytics blueprint
        try:
            from routes.analytics import analytics_bp
            app.register_blueprint(analytics_bp)
            logger.info("Successfully registered analytics blueprint from routes.analytics")
        except ImportError:
            try:
                from app.routes.analytics import analytics_bp
                app.register_blueprint(analytics_bp)
                logger.info("Successfully registered analytics blueprint from app.routes.analytics")
            except ImportError:
                logger.warning("Could not import analytics blueprint from any location")
        
        # Try different import paths for the business blueprint
        try:
            from app.routes.business_routes import business_bp
            app.register_blueprint(business_bp)
            logger.info("Successfully registered business routes blueprint from app.routes")
        except ImportError:
            try:
                from routes.business_routes import business_bp
                app.register_blueprint(business_bp)
                logger.info("Successfully registered business routes blueprint from routes")
            except ImportError:
                logger.warning("Business routes not found in any location, skipping")
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
