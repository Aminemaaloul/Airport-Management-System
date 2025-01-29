from . import db
from datetime import datetime

# User Model
class User(db.Model):
    """
    Represents a user in the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user")  # Role: user or admin
    # Relationship to Assistance Requests
    assistance_requests = db.relationship('AssistanceRequest', backref='user', lazy=True)
    # Relationship to Notifications
    notifications = db.relationship('Notification', backref='user', lazy=True)
    # Relationship to Parking Reservations
    parking_reservations = db.relationship('ParkingReservation', backref='user', lazy=True)
    # Track flights the user is subscribed to
    subscriptions = db.relationship('FlightSubscription', backref='user', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

# Flight Model
class Flight(db.Model):
    """
    Represents a flight in the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    departure_airport = db.Column(db.String(10), nullable=False)  # IATA code
    arrival_airport = db.Column(db.String(10), nullable=False)  # IATA code
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled")  # Status: scheduled, delayed, canceled
    airline = db.Column(db.String(50), nullable=False)
    delay = db.Column(db.Integer, nullable=True)  # Delay in minutes
    delay_reason = db.Column(db.String(200), nullable=True)
    # Relationship to Baggage
    baggage = db.relationship('Baggage', backref='flight', lazy=True)
    # Relationship to Subscriptions
    subscriptions = db.relationship('FlightSubscription', backref='flight', lazy=True)
    def serialize(self):
        return {
            'id': self.id,
            'flight_number': self.flight_number,
            'departure_airport': self.departure_airport,
            'arrival_airport': self.arrival_airport,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'status': self.status,
            'airline': self.airline,
            'delay': self.delay,
            'delay_reason': self.delay_reason
        }

# Baggage Model
class Baggage(db.Model):
    """
    Represents baggage associated with a flight.
    """
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)  # Associated flight
    baggage_tag = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="checked-in")  # Status: checked-in, in transit, delivered, lost
    last_updated = db.Column(db.DateTime, nullable=False)
    def serialize(self):
        return {
            'id': self.id,
            'flight_id': self.flight_id,
            'baggage_tag': self.baggage_tag,
            'status': self.status,
            'last_updated': self.last_updated.isoformat()
        }

# Assistance Request Model
class AssistanceRequest(db.Model):
    """
    Represents a passenger assistance request.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=True)  # Optional associated flight
    request_type = db.Column(db.String(50), nullable=False)  # Type: wheelchair, special meal
    status = db.Column(db.String(50), nullable=False, default="pending")  # Status: pending, in progress, completed
    timestamp = db.Column(db.DateTime, nullable=False)
    def serialize(self):
       return {
           'id': self.id,
           'user_id': self.user_id,
           'flight_id': self.flight_id,
           'request_type': self.request_type,
           'status': self.status,
           'timestamp': self.timestamp.isoformat()
       }

# Parking Reservation Model
class ParkingReservation(db.Model):
    """
    Represents a parking reservation for a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User making the reservation
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)  # Reserved spot
    reservation_time = db.Column(db.DateTime, nullable=False)  # Time the reservation was made
    status = db.Column(db.String(20), nullable=False, default="reserved")  # Status: reserved, canceled
    def serialize(self):
       return {
           'id': self.id,
           'user_id': self.user_id,
           'parking_spot_id': self.parking_spot_id,
           'reservation_time': self.reservation_time.isoformat(),
           'status': self.status
       }

# Parking Spot Model
class ParkingSpot(db.Model):
    """
    Represents a parking spot in the airport.
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)  # Parking spot location (e.g., "A1")
    status = db.Column(db.String(20), nullable=False, default="available")  # Status: available, reserved, occupied
    reservations = db.relationship('ParkingReservation', backref='parking_spot', lazy=True)
    def serialize(self):
       return {
           'id': self.id,
           'location': self.location,
           'status': self.status
       }

# Notification Model
class Notification(db.Model):
    """
    Represents a notification sent to a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Associated user
    message = db.Column(db.String(200), nullable=False)
    flight_number = db.Column(db.String(20), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'flight_number': self.flight_number,
            'timestamp': self.timestamp.isoformat()
        }

# Flight Subscription Model
class FlightSubscription(db.Model):
    """
    Represents a subscription to a flight by a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Subscribed user
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)  # Subscribed flight
    def serialize(self):
       return {
           'id': self.id,
           'user_id': self.user_id,
           'flight_id': self.flight_id
       }