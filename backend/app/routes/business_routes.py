from flask import Blueprint, request, jsonify, current_app
from app.models.business import Business
from app.db import db
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
business_bp = Blueprint('business_bp', __name__, url_prefix='/api')

@business_bp.route('/businesses', methods=['GET', 'OPTIONS'])
def get_businesses():
    logger.info("HIT: /api/businesses route")
    """Get all businesses or a specific business by ID"""
    logger.info("GET /api/businesses endpoint called")
    
    # Handle CORS OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 204
    
    # Fallback business data that will be returned if database fails
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
        },
        {
            "id": "11111",
            "name": "Test Business",
            "description": "Test business for analytics",
            "domain": "test.com"
        }
    ]
    
    # Check if ID is provided as a query parameter
    business_id = request.args.get('id')
    
    try:
        if business_id:
            # If ID is provided, get that specific business
            logger.info(f"Fetching business with ID: {business_id}")
            business = Business.query.filter_by(id=business_id).first()
            
            if not business:
                logger.warning(f"Business with ID {business_id} not found, returning fallback data")
                # Try to find a matching ID in fallback data
                for fb in FALLBACK_BUSINESSES:
                    if fb["id"] == business_id:
                        return jsonify(fb)
                # If no match, modify first fallback to use requested ID
                fallback = FALLBACK_BUSINESSES[0].copy()
                fallback["id"] = business_id
                return jsonify(fallback)
                
            return jsonify({
                "id": business.id,
                "name": business.name,
                "description": business.description,
                "domain": getattr(business, "domain", None) or f"business-{business.id}.com"
            })
        else:
            # Otherwise, get all businesses
            logger.info("Fetching all businesses")
            businesses = Business.query.all()
            if businesses:
                return jsonify([{
                    "id": business.id,
                    "name": business.name,
                    "description": business.description,
                    "domain": getattr(business, "domain", None) or f"business-{business.id}.com"
                } for business in businesses])
            else:
                # Return fallback data if no businesses in database
                logger.warning("No businesses found in database, returning fallback data")
                return jsonify(FALLBACK_BUSINESSES)
            
    except Exception as e:
        logger.error(f"Error fetching businesses: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Return fallback data on any exception
        logger.info("Returning fallback business data due to error")
        if business_id:
            for fb in FALLBACK_BUSINESSES:
                if fb["id"] == business_id:
                    return jsonify(fb)
            fallback = FALLBACK_BUSINESSES[0].copy()
            fallback["id"] = business_id
            return jsonify(fallback)
        else:
            return jsonify(FALLBACK_BUSINESSES)

@business_bp.route('/businesses', methods=['POST'])
def create_business():
    """Create a new business"""
    logger.info("POST /api/businesses endpoint called")
    
    try:
        data = request.json
        logger.info(f"Received business data: {data}")
        
        # Validate required fields
        if 'id' not in data or 'name' not in data:
            logger.error("Missing required fields: id and name")
            return jsonify({"error": "Missing required fields: id and name"}), 400
            
        # Always treat business ID as string for database operations
        business_id = str(data['id'])
                
        # Check if business already exists
        existing_business = Business.query.filter_by(id=business_id).first()
        if existing_business:
            logger.warning(f"Business with ID {business_id} already exists")
            return jsonify({"error": "Business with this ID already exists"}), 409
            
        # Create new business
        business = Business(
            id=business_id,  # Store as string
            name=data['name'],
            description=data.get('description', f"Business {business_id}"),
            domain=data.get('domain', f"business-{business_id}.com")  # Add default domain
        )
        
        db.session.add(business)
        db.session.commit()
        
        logger.info(f"Created new business with ID: {business.id}")
        
        return jsonify({
            "id": business.id,
            "name": business.name,
            "description": business.description
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating business: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@business_bp.route('/businesses/<business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business by ID"""
    logger.info(f"GET /api/businesses/{business_id} endpoint called")
    
    try:
        business = Business.query.filter_by(id=business_id).first()
        
        if not business:
            logger.warning(f"Business with ID {business_id} not found")
            return jsonify({"error": "Business not found"}), 404
            
        return jsonify({
            "id": business.id,
            "name": business.name,
            "description": business.description
        })
        
    except Exception as e:
        logger.error(f"Error fetching business: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
