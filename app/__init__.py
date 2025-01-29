from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
import requests
from .error_handler import handle_api_error


# Load environment variables from .env file
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

# Initialize JWTManager
jwt = JWTManager()

# Initialize Flask-Mail
mail = Mail()

def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)

    # Load configuration from .env file
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use the same secret key for JWT

    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app and db
    jwt.init_app(app)
    mail.init_app(app)

    # Import models (ensure this is done after db initialization)
    from .models import User, Flight, Baggage, AssistanceRequest, ParkingSpot, Notification

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.flights import flights_bp
    from .routes.baggage import baggage_bp
    from .routes.assistance import assistance_bp
    from .routes.parking import parking_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(baggage_bp)
    app.register_blueprint(assistance_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(admin_bp)
    
    app.register_error_handler(requests.exceptions.RequestException, handle_api_error)

    return app