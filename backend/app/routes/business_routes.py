from flask import Blueprint, request, jsonify, current_app
from app.models.business import Business
from app.db import db
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
business_bp = Blueprint('business_bp', __name__)

@business_bp.route('/api/businesses', methods=['GET'])
def get_businesses():
    """Get all businesses or a specific business by ID"""
    logger.info("GET /api/businesses endpoint called")
    
    # Check if ID is provided as a query parameter
    business_id = request.args.get('id')
    
    try:
        if business_id:
            # If ID is provided, get that specific business
            logger.info(f"Fetching business with ID: {business_id}")
            # Ensure business_id is a string for database lookup
            business = Business.query.filter_by(id=str(business_id)).first()
            
            if not business:
                logger.warning(f"Business with ID {business_id} not found")
                return jsonify({"error": "Business not found"}), 404
                
            return jsonify({
                "id": business.id,
                "name": business.name,
                "description": business.description
            })
        else:
            # Otherwise, get all businesses
            logger.info("Fetching all businesses")
            businesses = Business.query.all()
            return jsonify([{
                "id": business.id,
                "name": business.name,
                "description": business.description
            } for business in businesses])
            
    except Exception as e:
        logger.error(f"Error fetching businesses: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@business_bp.route('/api/businesses', methods=['POST'])
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
            
        # Make sure ID is an integer
        try:
            business_id = int(data['id'])
            # Convert to string for database lookup
            business_id_str = str(business_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid business_id format: {data['id']}. Must be a valid integer.")
            return jsonify({"error": "Business ID must be a valid integer"}), 400
                
        # Check if business already exists
        existing_business = Business.query.filter_by(id=business_id_str).first()
        if existing_business:
            logger.warning(f"Business with ID {business_id} already exists")
            return jsonify({"error": "Business with this ID already exists"}), 409
            
        # Create new business
        business = Business(
            id=business_id_str,  # Store as string
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

@business_bp.route('/api/businesses/<business_id>', methods=['GET'])
def get_business(business_id):
    """Get a specific business by ID"""
    logger.info(f"GET /api/businesses/{business_id} endpoint called")
    
    try:
        # Ensure business_id is a string for database lookup
        business = Business.query.filter_by(id=str(business_id)).first()
        
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
