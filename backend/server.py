from app import create_app
import os

app = create_app()

@app.route('/')
@app.route('/health')
@app.route('/healthz')
@app.route('/_health')
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
