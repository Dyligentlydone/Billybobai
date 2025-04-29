import logging
from flask import Blueprint, request, jsonify
from app.db import db
from app.models import Business, ClientPasscode
import json

logger = logging.getLogger(__name__)

# Blueprint: /api/clients
clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")

# --- Utility --------------------------------------------------------------
ADMIN_TOKEN = "97225"

def _is_admin_request(req):
    """Return True if the incoming request is authenticated as an admin."""
    # Query param ?admin=<token> or ?admin_token=<token>
    admin_query = req.args.get("admin") or req.args.get("admin_token")
    # Cookie-based auth (legacy)
    admin_cookie = req.cookies.get("admin_password")
    # Authorization header (Bearer <token> or raw token)
    auth_header = req.headers.get("Authorization")
    auth_token = None
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            auth_token = parts[1]
        else:
            auth_token = auth_header

    return ADMIN_TOKEN in {admin_query, admin_cookie, auth_token}

# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------

@clients_bp.route("", methods=["GET"])  # /api/clients?business_id=<id>
def list_clients():
    """List all client passcodes for a business (admin only)."""
    logger.info("/api/clients GET hit")

    if not _is_admin_request(request):
        logger.warning("Unauthorized list_clients attempt")
        return jsonify({"message": "Unauthorized", "clients": []}), 401

    business_id = request.args.get("business_id")
    if not business_id:
        return jsonify({"message": "Business ID is required", "clients": []}), 400

    if business_id == "admin":  # Special case used elsewhere in codebase
        return jsonify({"clients": []}), 200

    try:
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            return jsonify({"message": "Business not found", "clients": []}), 404

        passcodes = (
            db.session.query(ClientPasscode)
            .filter_by(business_id=business_id)
            .all()
        )
        return jsonify({"clients": [p.to_dict() for p in passcodes]}), 200
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        return jsonify({"message": f"Error listing clients: {str(e)}", "clients": []}), 500


@clients_bp.route("", methods=["POST"])  # /api/clients
def create_client():
    """Create a new client passcode (admin only)."""
    logger.info("/api/clients POST hit")

    if not _is_admin_request(request):
        return jsonify({"message": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json() or {}
    business_id = data.get("business_id")
    passcode_value = data.get("passcode")
    permissions = data.get("permissions", {})

    # Validate required fields
    if not business_id:
        return jsonify({"message": "Business ID is required"}), 400
    if not passcode_value:
        return jsonify({"message": "Passcode is required"}), 400

    try:
        business = db.session.query(Business).filter_by(id=business_id).first()
        if not business:
            return jsonify({"message": "Business not found"}), 404

        # Ensure passcode uniqueness per business
        existing = (
            db.session.query(ClientPasscode)
            .filter_by(business_id=business_id, passcode=passcode_value)
            .first()
        )
        if existing:
            return jsonify({"message": "Passcode already exists"}), 409

        # Normalise permissions -> dict
        if isinstance(permissions, str):
            try:
                permissions = json.loads(permissions)
            except json.JSONDecodeError:
                logger.warning("Invalid permissions JSON string; defaulting to empty dict")
                permissions = {}
        elif not isinstance(permissions, dict):
            permissions = {}

        new_client = ClientPasscode(
            business_id=business_id,
            passcode=passcode_value,
            permissions=permissions,
        )
        db.session.add(new_client)
        db.session.commit()
        logger.info("Created new client passcode %s for business %s", passcode_value, business_id)
        return jsonify({"client": new_client.to_dict(), "message": "Client created"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating client: {e}")
        return jsonify({"message": f"Error creating client: {str(e)}"}), 500


@clients_bp.route("/<int:client_id>/permissions", methods=["PUT"])  # /api/clients/<id>/permissions
def update_permissions(client_id):
    """Update permissions for a client passcode (admin only)."""
    logger.info("PUT /api/clients/%s/permissions", client_id)

    if not _is_admin_request(request):
        return jsonify({"message": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.get_json() or {}
    permissions = data.get("permissions")
    if permissions is None:
        return jsonify({"message": "Permissions field is required"}), 400

    # Normalise permissions to dict
    if isinstance(permissions, str):
        try:
            permissions = json.loads(permissions)
        except json.JSONDecodeError:
            return jsonify({"message": "Invalid permissions JSON"}), 400
    elif not isinstance(permissions, dict):
        return jsonify({"message": "Invalid permissions format"}), 400

    try:
        client = db.session.query(ClientPasscode).filter_by(id=client_id).first()
        if not client:
            return jsonify({"message": "Client not found"}), 404

        client.permissions = permissions
        db.session.commit()
        logger.info("Updated permissions for client %s", client_id)
        return jsonify({"client": client.to_dict(), "message": "Permissions updated"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating permissions: {e}")
        return jsonify({"message": f"Error updating permissions: {str(e)}"}), 500
