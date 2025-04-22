from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# No custom engine/session; let Flask-SQLAlchemy handle it
# All models should import db from here