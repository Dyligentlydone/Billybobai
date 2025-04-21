"""
This file is the main entry point for the Flask application.
It directly defines critical routes to ensure they're available.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import uuid
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    "https://billybobai-production-6713.up.railway.app",
    "https://billybobai-production.up.railway.app",
    "http://localhost:5173",
    "http://localhost:3000"
], supports_credentials=True)

# Import database and models
try:
    from app.db import db
    from app.models.workflow import Workflow
    logger.info("Successfully imported database and models")
except Exception as e:
    logger.error(f"Error importing database and models: {str(e)}")
    # Create fallback models if import fails
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    class Workflow(db.Model):
        __tablename__ = 'workflows'
        id = db.Column(db.String(255), primary_key=True)
        name = db.Column(db.String(255), nullable=False)
        status = db.Column(db.String(50), default='draft')
        client_id = db.Column(db.String(255))
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
        actions = db.Column(db.JSON, default={})
        conditions = db.Column(db.JSON, default={})

# Import the rest of the application
try:
    from app import create_app
    main_app = create_app()
    # Register all blueprints from main_app to this app
    for blueprint in main_app.blueprints.values():
        app.register_blueprint(blueprint)
    logger.info("Successfully imported and registered blueprints from app package")
except Exception as e:
    logger.error(f"Error importing app package: {str(e)}")

# Define critical routes directly to ensure they're available
@app.route('/health')
def health():
    """Health check endpoint that returns registered routes."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': [method for method in rule.methods if method not in ['HEAD', 'OPTIONS']],
            'path': str(rule)
        })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'routes': routes
    })

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows."""
    logger.info("GET /api/workflows endpoint called directly")
    try:
        workflows = Workflow.query.all()
        return jsonify([{
            '_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'actions': workflow.actions,
            'conditions': workflow.conditions,
            'createdAt': workflow.created_at.isoformat(),
            'updatedAt': workflow.updated_at.isoformat()
        } for workflow in workflows])
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow."""
    logger.info("POST /api/workflows endpoint called directly")
    try:
        # Log the request details
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        
        # Get the request data
        data = request.json
        logger.info(f"Received workflow data: {data}")
        
        # Generate a UUID for the workflow
        workflow_id = str(uuid.uuid4())
        
        # Create the workflow
        workflow = Workflow(
            id=workflow_id,
            name=data.get('name', 'New Workflow'),
            status='draft',
            actions=data.get('actions', {}),
            conditions=data.get('conditions', {}),
            client_id=data.get('business_id'),  # Map business_id from frontend to client_id in database
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Log the workflow object
        logger.info(f"Created workflow object: {workflow}")
        
        # Save the workflow to the database
        db.session.add(workflow)
        db.session.commit()
        logger.info(f"Workflow created with ID: {workflow.id}")
        
        # Return the workflow
        return jsonify({
            '_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'actions': workflow.actions,
            'conditions': workflow.conditions,
            'createdAt': workflow.created_at.isoformat(),
            'updatedAt': workflow.updated_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
