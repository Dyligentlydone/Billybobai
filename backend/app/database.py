"""
Database module for the application.
This module provides the database connection and session management.
"""
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    from .models.workflow import Workflow
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return db
