from flask import Blueprint, request, jsonify, g
import logging
from app.models import Business, ClientPasscode
from app.db import db

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/auth/passcodes', methods=['GET'])
def get_passcodes():
    """Get all client passcodes for the authenticated business."""
    logger.info("Fetching client passcodes")
    try:
        # Check if admin session is active
        admin_password = request.cookies.get('admin_password')
        if not admin_password or admin_password != "97225":  # Your admin password
            logger.warning("Unauthorized access attempt to passcodes")
            return jsonify({"message": "Unauthorized access"}), 401
            
        # Get business ID from request
        business_id = request.args.get('business_id')
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required"}), 400
            
        # Query passcodes for the business
        passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
        
        # Convert to dictionary for JSON response
        passcode_list = [passcode.to_dict() for passcode in passcodes]
        
        return jsonify({"clients": passcode_list}), 200
    except Exception as e:
        logger.error(f"Error fetching passcodes: {str(e)}")
        return jsonify({"message": f"Error fetching passcodes: {str(e)}"}), 500

@auth_bp.route('/api/auth/passcodes', methods=['POST'])
def create_passcode():
    """Create a new client access passcode."""
    logger.info("Creating new client passcode")
    try:
        # Check if admin session is active
        admin_password = request.cookies.get('admin_password')
        if not admin_password or admin_password != "97225":  # Your admin password
            logger.warning("Unauthorized access attempt to create passcode")
            return jsonify({"message": "Unauthorized access"}), 401
            
        # Parse request data
        data = request.get_json()
        
        if not data:
            logger.warning("No data provided for passcode creation")
            return jsonify({"message": "No data provided"}), 400
            
        business_id = data.get('business_id')
        passcode = data.get('passcode')
        permissions = data.get('permissions')
        
        # Validate required fields
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required"}), 400
            
        if not passcode:
            logger.warning("Passcode not provided")
            return jsonify({"message": "Passcode is required"}), 400
            
        if not permissions:
            logger.warning("Permissions not provided")
            return jsonify({"message": "Permissions are required"}), 400
            
        # Validate passcode format (5 digits)
        if len(passcode) != 5 or not passcode.isdigit():
            logger.warning(f"Invalid passcode format: {passcode}")
            return jsonify({"message": "Passcode must be 5 digits"}), 400
            
        # Check if business exists
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            return jsonify({"message": "Business not found"}), 404
            
        # Check if passcode already exists
        existing_passcode = db.session.query(ClientPasscode).filter_by(
            business_id=business_id, passcode=passcode).first()
        if existing_passcode:
            logger.warning(f"Passcode already exists for business {business_id}")
            return jsonify({"message": "Passcode already exists for this business"}), 409
            
        # Create new client passcode
        new_passcode = ClientPasscode(
            business_id=business_id,
            passcode=passcode,
            permissions=permissions
        )
        
        # Add to database
        db.session.add(new_passcode)
        db.session.commit()
        
        logger.info(f"Created new client passcode for business {business_id}")
        return jsonify({"message": "Client access created successfully", "id": new_passcode.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating passcode: {str(e)}")
        return jsonify({"message": f"Error creating client access: {str(e)}"}), 500

@auth_bp.route('/api/auth/passcodes/<int:passcode_id>', methods=['DELETE'])
def delete_passcode(passcode_id):
    """Delete a client access passcode."""
    logger.info(f"Deleting client passcode {passcode_id}")
    try:
        # Check if admin session is active
        admin_password = request.cookies.get('admin_password')
        if not admin_password or admin_password != "97225":  # Your admin password
            logger.warning("Unauthorized access attempt to delete passcode")
            return jsonify({"message": "Unauthorized access"}), 401
            
        # Find passcode
        passcode = db.session.query(ClientPasscode).filter_by(id=passcode_id).first()
        if not passcode:
            logger.warning(f"Passcode not found: {passcode_id}")
            return jsonify({"message": "Passcode not found"}), 404
            
        # Delete passcode
        db.session.delete(passcode)
        db.session.commit()
        
        logger.info(f"Deleted client passcode {passcode_id}")
        return jsonify({"message": "Client access deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting passcode: {str(e)}")
        return jsonify({"message": f"Error deleting client access: {str(e)}"}), 500
