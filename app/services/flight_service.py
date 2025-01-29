import requests
import os
from datetime import datetime
from app.models import db, Flight

# Load API key from environment variables
AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY')

def save_flight(flight_data):
    """
    Save or update flight data to the database.
    """
    try:
        # Check if the flight already exists in the database
        flight = Flight.query.filter_by(flight_number=flight_data['flight_number']).first()

        if flight:
            # Update the existing flight record
            flight.departure_airport = flight_data['departure_airport']
            flight.arrival_airport = flight_data['arrival_airport']
            flight.departure_time = datetime.fromisoformat(flight_data['scheduled_departure'])
            flight.arrival_time = datetime.fromisoformat(flight_data['estimated_departure'])
            flight.status = flight_data.get('status', 'scheduled')
            flight.airline = flight_data['airline']
        else:
            # If the flight doesn't exist, create a new Flight record
            flight = Flight(
                flight_number=flight_data['flight_number'],
                departure_airport=flight_data['departure_airport'],
                arrival_airport=flight_data['arrival_airport'],
                departure_time=datetime.fromisoformat(flight_data['scheduled_departure']),
                arrival_time=datetime.fromisoformat(flight_data['estimated_departure']),
                status=flight_data.get('status', 'scheduled'),  # Default status if not provided
                airline=flight_data['airline']
            )
            db.session.add(flight)
        db.session.commit()

        return flight
    except Exception as e:
        db.session.rollback()
        print(f"Error saving flight data: {e}")
        return None

def fetch_flight_data(flight_number=None, date=None):
    """
    Fetch flight data from the Aviationstack API.
    """
    base_url = "http://api.aviationstack.com/v1/flights"
    headers = {"Authorization": f"Bearer {AVIATIONSTACK_API_KEY}"}

    params = {}
    if flight_number:
        params["flight_number"] = flight_number
    if date:
        params["date"] = date

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
         # Save flight data to the database
        flights = []
        for flight in data.get('data', []):
          flight_info = {
                "flight_number": flight['flight']['iata'],
                "departure_airport": flight['departure']['iata'],
                "arrival_airport": flight['arrival']['iata'],
                "scheduled_departure": flight['departure']['scheduled'],
                "estimated_departure": flight['departure']['estimated'],
                "status": flight['flight_status'],  # Use the flight status from the API
                "airline": flight['airline']['name'],  # Use the airline name from the API
            }
          
          saved_flight = save_flight(flight_info)
          if saved_flight:
            flights.append(saved_flight.serialize())

        return flights
    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {e}")
        return None