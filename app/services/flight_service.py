import requests
import os
from datetime import datetime
from app.models import db, Flight

# Load API key from environment variables
AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY')

# Define Tunis Carthage airport IATA code
TUNIS_CARTHAGE_IATA = "TUN"

def save_flight(flight_data):
    """
    Save or update flight data to the database.
    """
    try:
        print("Saving flight data:", flight_data)
        # Check if the flight already exists in the database
        flight = Flight.query.filter_by(flight_number=flight_data['flight_number']).first()
        print("Existing flight:", flight)

        if flight:
            # Update the existing flight record
            flight.departure_airport = flight_data['departure_airport']
            flight.arrival_airport = flight_data['arrival_airport']
            flight.departure_time = datetime.fromisoformat(flight_data['scheduled_departure'])
            flight.arrival_time = datetime.fromisoformat(flight_data.get('scheduled_arrival', flight_data['scheduled_departure']))
            flight.status = flight_data.get('status', 'scheduled')
            flight.airline = flight_data['airline']
        else:
            # If the flight doesn't exist, create a new Flight record
            flight = Flight(
                flight_number=flight_data['flight_number'],
                departure_airport=flight_data['departure_airport'],
                arrival_airport=flight_data['arrival_airport'],
                departure_time=datetime.fromisoformat(flight_data['scheduled_departure']),
                arrival_time=datetime.fromisoformat(flight_data.get('scheduled_arrival', flight_data['scheduled_departure'])),
                status=flight_data.get('status', 'scheduled'),  # Default status if not provided
                airline=flight_data['airline']
            )
            db.session.add(flight)
        db.session.commit()
        print("Flight saved successfully:", flight.serialize())
        return flight.serialize()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving flight data: {e}")
        return None

def fetch_flight_data_tunis(flight_number=None, date=None):
    """
    Fetch flight data for Tunis Carthage Airport (departures and arrivals) from the Aviationstack API.
    """
    base_url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}"

    # Add parameters for departures and arrivals
    departure_url = base_url + f"&dep_iata={TUNIS_CARTHAGE_IATA}"
    arrival_url = base_url + f"&arr_iata={TUNIS_CARTHAGE_IATA}"

    if date:
        departure_url += f"&date={date}"
        arrival_url += f"&date={date}"
    if flight_number:
        departure_url += f"&flight_number={flight_number}"
        arrival_url += f"&flight_number={flight_number}"

    flights = []

    try:
        # Fetch departure flights
        print(f"Fetching departures from API: {departure_url}")
        departure_response = requests.get(departure_url)
        print(f"Departure API Response Status Code: {departure_response.status_code}")
        print(f"Departure API Response Text: {departure_response.text}")
        departure_response.raise_for_status()
        departure_data = departure_response.json()

        for flight in departure_data.get('data', []):
            flight_info = {
                "flight_number": flight['flight']['iata'],
                "departure_airport": flight['departure']['iata'],
                "arrival_airport": flight['arrival']['iata'],
                "scheduled_departure": flight['departure']['scheduled'],
                "scheduled_arrival": flight['arrival']['scheduled'],
                "status": flight['flight_status'],
                "airline": flight['airline']['name'],
            }
            saved_flight = save_flight(flight_info) # Save departure flights
            if saved_flight:
                flights.append(saved_flight) # append saved flights


        # Fetch arrival flights
        print(f"Fetching arrivals from API: {arrival_url}")
        arrival_response = requests.get(arrival_url)
        print(f"Arrival API Response Status Code: {arrival_response.status_code}")
        print(f"Arrival API Response Text: {arrival_response.text}")
        arrival_response.raise_for_status()
        arrival_data = arrival_response.json()

        for flight in arrival_data.get('data', []):
            flight_info = {
                "flight_number": flight['flight']['iata'],
                "departure_airport": flight['departure']['iata'],
                "arrival_airport": flight['arrival']['iata'],
                "scheduled_departure": flight['departure']['scheduled'],
                "scheduled_arrival": flight['arrival']['scheduled'],
                "status": flight['flight_status'],
                "airline": flight['airline']['name'],
            }
            saved_flight = save_flight(flight_info) # Save arrival flights
            if saved_flight:
                 flights.append(saved_flight) # append saved flights

        print(f"Flights after API call: {flights}")
        return flights

    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {e}")
        return None