"""
This file is the main entry point for the Flask application.
It imports the app from the app package and serves it.
"""
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
