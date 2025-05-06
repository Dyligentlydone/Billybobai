import os
from flask import Flask
from app.db import db
from sqlalchemy import text

# Create a minimal Flask app for the database connection
app = Flask(__name__)

# Get the DATABASE_URL from the environment or use a default
database_url = os.environ.get('DATABASE_URL', None)
if not database_url:
    # Check if there's a .env file with the DATABASE_URL
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip().strip('"\'')
                    break
    except:
        pass

# If still no DATABASE_URL, ask for it
if not database_url:
    print("Please enter your Railway PostgreSQL connection string:")
    database_url = input("> ")

# Configure Flask app with the database URL
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Add the unique constraint
with app.app_context():
    try:
        # Execute the ALTER TABLE command
        db.session.execute(text("""
        ALTER TABLE sms_consents 
        ADD CONSTRAINT uq_sms_consent_phone_business 
        UNIQUE (phone_number, business_id);
        """))
        db.session.commit()
        print("Successfully added unique constraint to sms_consents table!")
    except Exception as e:
        print(f"Error adding constraint: {e}")
        # If it fails because the constraint already exists, that's okay
        if "already exists" in str(e):
            print("The constraint might already exist, which is fine.")
