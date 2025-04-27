from flask import Blueprint, request, jsonify, g
import logging
from app.models import Business, ClientPasscode
from app.db import db
import json

logger = logging.getLogger(__name__)

# Create Flask blueprint
auth = Blueprint('auth', __name__, url_prefix='/api')
# Define the original auth_bp for backward compatibility, but we'll mainly use 'auth'
auth_bp = auth

@auth.route('/auth/passcodes', methods=['GET'])
def get_passcodes():
    """Get all client passcodes for the authenticated business."""
    logger.info("Fetching client passcodes")
    try:
        # Check admin authentication from different sources
        admin_password = request.cookies.get('admin_password')
        auth_header = request.headers.get('Authorization')
        admin_query = request.args.get('admin')
        
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Cookies: {request.cookies}")
        logger.info(f"Auth header: {auth_header}")
        logger.info(f"Admin query: {admin_query}")
        
        is_admin = (admin_password == "97225" or 
                   (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                   admin_query == "97225")
        
        if not is_admin:
            logger.warning("Unauthorized access attempt to get passcodes")
            return jsonify({"message": "Unauthorized access - admin authentication required"}), 401
            
        # Get business ID from request
        business_id = request.args.get('business_id')
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required", "clients": []}), 200
        
        # Special handling for admin business_id - should succeed even if no real business exists with this ID
        if business_id == 'admin':
            logger.info("Admin used as business_id - returning empty client list")
            return jsonify({"message": "Success", "clients": []}), 200
            
        # Check if business exists - important validation step added back from earlier commits
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business ID not found: {business_id}")
            return jsonify({"message": "Success", "clients": []}), 200  # Return 200 to avoid frontend errors
                
        # Query passcodes for the business
        passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
        
        # Convert to dictionary for JSON response
        passcode_list = [passcode.to_dict() for passcode in passcodes]
        
        return jsonify({"clients": passcode_list}), 200
    except Exception as e:
        logger.error(f"Error fetching passcodes: {str(e)}")
        return jsonify({"message": f"Error fetching passcodes: {str(e)}"}), 500

@auth.route('/auth/passcodes', methods=['POST'])
def create_passcode():
    """Create a new client access passcode."""
    logger.info("Creating new client passcode")
    try:
        # Check admin authentication from different sources
        admin_password = request.cookies.get('admin_password')
        auth_header = request.headers.get('Authorization')
        admin_query = request.args.get('admin')
        
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Cookies: {request.cookies}")
        logger.info(f"Auth header: {auth_header}")
        logger.info(f"Admin query: {admin_query}")
        
        is_admin = (admin_password == "97225" or 
                   (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                   admin_query == "97225")
        
        if not is_admin:
            logger.warning("Unauthorized access attempt to create passcode")
            return jsonify({"message": "Unauthorized access - admin authentication required"}), 401
            
        # Parse request data
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            logger.warning("No data provided for passcode creation")
            return jsonify({"message": "No data provided"}), 400
            
        business_id = data.get('business_id')
        passcode = data.get('passcode')
        permissions = data.get('permissions')
        
        logger.info(f"Creating passcode for business_id: {business_id}, passcode: {passcode}")
        
        # Validate required fields
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required"}), 400
            
        if not passcode:
            logger.warning("Passcode not provided")
            return jsonify({"message": "Passcode is required"}), 400
            
        # Special handling for 'admin' as business_id
        if business_id == 'admin':
            logger.warning("Cannot create client access for business_id 'admin'")
            return jsonify({"message": "Invalid business ID"}), 400
            
        # Check if business exists - crucial validation step from earlier commits
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            return jsonify({"message": "Business not found"}), 404
            
        if not permissions:
            logger.warning("Permissions not provided")
            return jsonify({"message": "Permissions are required"}), 400
            
        # Validate passcode format (5 digits)
        if len(passcode) != 5 or not passcode.isdigit():
            logger.warning(f"Invalid passcode format: {passcode}")
            return jsonify({"message": "Passcode must be 5 digits"}), 400
            
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
        logger.exception("Detailed error information:") 
        return jsonify({"message": f"Error creating client access: {str(e)}"}), 500

@auth.route('/auth/passcodes/<int:passcode_id>', methods=['DELETE'])
def delete_passcode(passcode_id):
    """Delete a client access passcode."""
    logger.info(f"Deleting client passcode {passcode_id}")
    try:
        # Check admin authentication from different sources
        admin_password = request.cookies.get('admin_password')
        auth_header = request.headers.get('Authorization')
        admin_query = request.args.get('admin')
        
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Cookies: {request.cookies}")
        logger.info(f"Auth header: {auth_header}")
        logger.info(f"Admin query: {admin_query}")
        
        is_admin = (admin_password == "97225" or 
                   (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                   admin_query == "97225")
        
        if not is_admin:
            logger.warning("Unauthorized access attempt to delete passcode")
            return jsonify({"message": "Unauthorized access - admin authentication required"}), 401
            
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

@auth.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint for clients using passcodes"""
    logger.info("Client login attempt")
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No login data provided")
            return jsonify({"message": "No data provided"}), 400
            
        business_id = data.get('business_id')
        passcode = data.get('password')  # Frontend sends passcode as 'password'
        
        logger.info(f"Login attempt for business_id: {business_id}")
        
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID required"}), 400
            
        if not passcode:
            logger.warning("Passcode not provided")
            return jsonify({"message": "Passcode required"}), 400
        
        # Check if it's an admin login attempt
        if passcode == "97225":
            # Admin login
            logger.info(f"Admin login attempt for business: {business_id}")
            business = db.session.query(Business).filter_by(id=business_id).first()
            if business:
                logger.info(f"Admin login successful for business: {business_id}")
                return jsonify({
                    "business": {
                        "id": business.id,
                        "name": business.name,
                        "business_id": business.id,
                        "is_admin": True,
                        "domain": business.domain
                    },
                    "message": "Admin login successful"
                }), 200
            else:
                logger.warning(f"Business not found: {business_id}")
                return jsonify({"message": "Business not found"}), 404
                
        # Client login with passcode
        logger.info(f"Client login attempt with passcode for business: {business_id}")
        client = db.session.query(ClientPasscode).filter_by(
            business_id=business_id, passcode=passcode).first()
            
        if not client:
            logger.warning(f"Invalid passcode for business: {business_id}")
            return jsonify({"message": "Invalid business ID or passcode"}), 401
            
        # Get the business info
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            return jsonify({"message": "Business not found"}), 404
            
        # Return business with client permissions
        logger.info(f"Client login successful for business: {business_id}")
        return jsonify({
            "business": {
                "id": business.id,
                "name": business.name,
                "business_id": business.id,
                "is_admin": False,
                "domain": business.domain,
                "permissions": client.permissions
            },
            "message": "Login successful"
        }), 200
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"message": f"Error during login: {str(e)}"}), 500

@auth.route('/direct/client-access', methods=['POST', 'GET', 'OPTIONS'])
def direct_client_access():
    """Direct handler for client access with a unique route path."""
    logger.info(f"Direct client access handler via blueprint: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Handle OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 204
    
    # For GET requests, use the existing get_passcodes logic
    if request.method == 'GET':
        return get_passcodes()
    
    # For POST requests, use the existing create_passcode logic  
    if request.method == 'POST':
        return create_passcode()

@auth.route('/auth/direct-clients', methods=['GET', 'POST', 'OPTIONS'])
def direct_clients():
    """Direct handler for client access without query params to avoid Railway routing issues."""
    logger.info("Direct clients route hit")
    logger.info(f"Method: {request.method}, Headers: {dict(request.headers)}")
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
        
        logger.info(f"Direct clients for business_id: {business_id}, admin token: {admin_token}")
        
        is_admin = (admin_password == "97225" or 
                   (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                   admin_token == "97225")
        
        if not is_admin:
            logger.warning("Unauthorized access attempt to direct-clients")
            return jsonify({"message": "Unauthorized", "clients": []}), 200
            
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required", "clients": []}), 200
        
        # Special handling for 'admin' as business_id
        if business_id == 'admin':
            logger.info("Admin business_id - returning empty client list")
            return jsonify({"message": "Success", "clients": []}), 200
            
        # Check if business exists
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            return jsonify({"message": "Success", "clients": []}), 200
                
        # Query passcodes for the business
        passcodes = db.session.query(ClientPasscode).filter_by(business_id=business_id).all()
        
        # Convert to dictionary for JSON response
        passcode_list = [passcode.to_dict() for passcode in passcodes]
        
        return jsonify({"clients": passcode_list}), 200
    except Exception as e:
        logger.error(f"Error in direct_clients: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"message": "Error fetching clients", "clients": []}), 200

@auth.route('/auth/direct-client-create', methods=['POST', 'OPTIONS'])
def direct_client_create():
    """Direct handler for client access creation without query params to avoid Railway routing issues."""
    logger.info("Direct client create route hit")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Handle OPTIONS pre-flight requests
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 204
    
    try:
        # Check admin authentication from different sources
        admin_password = request.cookies.get('admin_password')
        auth_header = request.headers.get('Authorization')
        
        # Get data from request body
        if not request.is_json:
            logger.warning("Request is not JSON")
            return jsonify({"message": "Invalid request format"}), 400
            
        data = request.get_json()
        admin_token = data.get('admin_token') if data else None
        # Fallback to query param ?admin= for compatibility with frontend
        if not admin_token:
            admin_token = request.args.get('admin')
        business_id = data.get('business_id') if data else None
        passcode = data.get('passcode') if data else None
        permissions = data.get('permissions') if data else None
        
        logger.info(f"Direct client create for business_id: {business_id}, passcode: {passcode}")
        
        # Check authentication
        is_admin = (admin_password == "97225" or 
                   (auth_header and auth_header.replace('Bearer ', '') == "97225") or
                   admin_token == "97225")
        
        if not is_admin:
            logger.warning("Unauthorized access attempt to create client")
            return jsonify({"message": "Unauthorized"}), 401
            
        # Validate required fields
        if not business_id:
            logger.warning("Business ID not provided")
            return jsonify({"message": "Business ID is required"}), 400
            
        if not passcode:
            logger.warning("Passcode not provided")
            return jsonify({"message": "Passcode is required"}), 400
            
        # Special handling for 'admin' as business_id
        if business_id == 'admin':
            logger.warning("Cannot create client access for business_id 'admin'")
            return jsonify({"message": "Invalid business ID"}), 400
            
        # Check if business exists
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            return jsonify({"message": "Business not found"}), 404
            
        if not permissions:
            logger.warning("Permissions not provided")
            return jsonify({"message": "Permissions are required"}), 400
            
        if not passcode.isdigit() or len(passcode) != 5:
            logger.warning(f"Invalid passcode format: {passcode}")
            return jsonify({"message": "Passcode must be 5 digits"}), 400
            
        # Check if passcode already exists
        existing_passcode = db.session.query(ClientPasscode).filter_by(
            business_id=business_id, passcode=passcode).first()
        if existing_passcode:
            logger.warning(f"Passcode already exists: {passcode}")
            return jsonify({"message": "Passcode already exists"}), 409
            
        # Create new passcode
        try:
            # Ensure permissions is properly formatted as JSON string
            if isinstance(permissions, dict):
                permissions_json = json.dumps(permissions)
            elif isinstance(permissions, str):
                # Validate it can be parsed as JSON
                json.loads(permissions)
                permissions_json = permissions
            else:
                logger.warning(f"Invalid permissions format: {type(permissions)}")
                return jsonify({"message": "Invalid permissions format"}), 400
                
            new_passcode = ClientPasscode(
                business_id=business_id,
                passcode=passcode,
                permissions=permissions_json
            )
            db.session.add(new_passcode)
            db.session.commit()
            logger.info(f"Created new passcode: {passcode} for business: {business_id}")
            return jsonify({"message": "Client access created successfully"}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating passcode: {str(e)}")
            return jsonify({"message": f"Error creating client access: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Error in direct_client_create: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"message": f"Error: {str(e)}"}), 500
