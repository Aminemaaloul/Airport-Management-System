from flask import current_app
from flask_mail import Message
from app.models import Notification, User, db
from datetime import datetime

def send_notification(user_id, message, flight_number=None):
    """
    Send a notification to a user (and optionally send an email).
    """
    # Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    # Create a new notification record
    notification = Notification(
        user_id=user_id,
        flight_number=flight_number,  # Optional: Associate with a flight
        message=message,
        timestamp=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()

    # Send an email notification (optional)
    send_email_notification(user.email, message)

def send_email_notification(email, message):
    """
    Send an email notification using Flask-Mail.
    """
    msg = Message(
        subject="Flight Disruption Alert",
        recipients=[email],
        body=message
    )
    current_app.mail.send(msg)