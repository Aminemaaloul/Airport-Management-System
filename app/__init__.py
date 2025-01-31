from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
from flasgger import Swagger
from flask_smorest import Api  # Import Flask-Smorest

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

# Initialize Flask-Smorest
api = Api()  # Create an instance of the Api class

# Initialize Flasgger
swagger = Swagger()

def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)

    # Load configuration from .env file
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use the same secret key for JWT

    # Configure Flask-Smorest
    app.config['API_TITLE'] = 'Airport Management API'
    app.config['API_VERSION'] = '1.0'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

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
    api.init_app(app)  # Initialize Flask-Smorest with the app
    swagger.init_app(app)  # Initialize Flasgger with the app

    # Import models (ensure this is done after db initialization)
    from .models import User, Flight, Baggage, AssistanceRequest, ParkingSpot, Notification, ParkingReservation, FlightSubscription

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.flights import flights_bp
    from .routes.baggage import baggage_bp
    from .routes.assistance import assistance_bp
    from .routes.parking import parking_bp
    from .routes.admin import admin_bp
    from .routes.notifications import notification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(baggage_bp)
    app.register_blueprint(assistance_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    return app
