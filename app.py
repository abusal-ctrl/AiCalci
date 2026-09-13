from flask import Flask, render_template
from config import Config
from backend.routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    
    @app.route("/")
    def index():
        return render_template("index.html")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)