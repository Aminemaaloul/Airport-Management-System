from app import db, create_app
from app.models import User, ParkingSpot
from werkzeug.security import generate_password_hash
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def seed_data():
    """Seeds the database with initial data."""
    app = create_app()
    with app.app_context():
        # Create Users
        users_data = [
            {"name": "nour ghazali", "password": "Nour123", "role": "user"},
            {"name": "aymen bouzaien", "password": "Aymen123", "role": "user"},
            {"name": "amal riahi", "password": "Amal123", "role": "user"}

        ]

        users = []
        for user_info in users_data:
            username = user_info["name"]
            email = f"{user_info['name'].lower().replace(' ', '.')}@gmail.com"
            password = user_info["password"]
            role = user_info["role"]
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_password, role=role)
            users.append(user)
            db.session.add(user)
            logging.info(f"Created user: username={username}, email={email}, password={password} role={role}")

        # Create Parking Spots
        parking_spots = []
        for _ in range(5):
            location = f"{chr(random.randint(65, 70))}{random.randint(1, 10)}"
            parking_spot = ParkingSpot(location=location)
            parking_spots.append(parking_spot)
            db.session.add(parking_spot)

        db.session.commit()
        logging.info("Database seeded with data")


if __name__ == '__main__':
    seed_data()