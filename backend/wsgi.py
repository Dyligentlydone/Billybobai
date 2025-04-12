from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "OK"

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
