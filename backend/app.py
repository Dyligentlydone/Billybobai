"""
This file is the main entry point for the Flask application.
It directly defines critical routes to ensure they're available.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import sys
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://billybobai-production-6713.up.railway.app",
    "https://billybobai-production.up.railway.app",
    "https://www.dyligent.xyz",
]
CORS(app, origins=origins, supports_credentials=True)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///whys.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
try:
    from app.database import init_db
    db = init_db(app)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# Import the rest of the application
try:
    from app import create_app
    main_app = create_app()
    # Register all blueprints from main_app to this app
    for blueprint_name, blueprint in main_app.blueprints.items():
        if blueprint_name not in app.blueprints:
            app.register_blueprint(blueprint)
    logger.info("Successfully imported and registered blueprints from app package")
except Exception as e:
    logger.error(f"Error importing app package: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

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
        'timestamp': str(datetime.utcnow()),
        'routes': routes
    })

# Direct workflow API routes to ensure they're always available
@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows."""
    logger.info("GET /api/workflows endpoint called directly in app.py")
    try:
        from app.models.workflow import Workflow
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
        logger.error(f"Error in get_workflows: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow."""
    logger.info("POST /api/workflows endpoint called directly in app.py")
    try:
        from app.models.workflow import Workflow
        import uuid
        
        # Log request details for debugging
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request content type: {request.content_type}")
        
        # Get JSON data from request
        data = request.json
        if not data:
            logger.error("No JSON data in request")
            return jsonify({"error": "No data provided"}), 400
            
        logger.info(f"Received workflow data: {json.dumps(data)}")
        
        # Generate a UUID for the workflow
        workflow_id = str(uuid.uuid4())
        logger.info(f"Generated workflow ID: {workflow_id}")
        
        # Create new workflow
        workflow = Workflow(
            id=workflow_id,
            name=data.get('name', 'Untitled Workflow'),
            status=data.get('status', 'draft'),
            client_id=data.get('business_id', data.get('client_id')),
            actions=data.get('actions', {}),
            conditions=data.get('conditions', {}),
            nodes=data.get('nodes', []),
            edges=data.get('edges', [])
        )
        
        # Add to database
        db.session.add(workflow)
        db.session.commit()
        logger.info(f"Workflow created successfully with ID: {workflow_id}")
        
        # Return the created workflow
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
        logger.error(f"Error in create_workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
