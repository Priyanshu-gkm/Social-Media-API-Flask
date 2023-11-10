from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth

db = SQLAlchemy()
ma = Marshmallow()

auth = HTTPBasicAuth()

def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    # Configs
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.environ.get("POSTGRES_USERNAME")}:{os.environ.get("PASSWORD")}@{os.environ.get("HOST")}/{os.environ.get("DB_NAME")}'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # For not complaining in the console
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app,{"/api":app})
    
    db.init_app(app)
    Migrate(app,db)
    ma.init_app(app)

    with app.app_context():
        from . import resources  # Import routes
        db.create_all()  # Create sql tables for our data models
    return app
