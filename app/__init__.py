from flask import Flask
from app.config.settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from app.api.routes import main
    app.register_blueprint(main)
    
    return app