from app import create_app
from app.models import db, Baggage, Flight, User
from datetime import datetime
import random
from sqlalchemy import text


app = create_app()

with app.app_context():
    # Truncate the Baggage table before seeding
    db.session.execute(text('DELETE FROM baggage'))
    db.session.commit()

    # Fetch existing flight ids to avoid foreign key conflicts
    flight_ids = [row.id for row in db.session.query(Flight.id).all()]


    if not flight_ids:
        print("Error: No flights found in the database. Please populate the Flight table before seeding baggage")
    else:
      # Fetch user ids with "user" role
        user_ids = [row.id for row in db.session.query(User.id).filter(User.role == 'user').all()]

        if not user_ids:
            print("Error: No users with 'user' role found in the database")

        elif len(user_ids) < 10:
            print("Error: Less than 10 users with 'user' role found in the database")
        else:
          baggages = []
          for i in range(10):
              user_id = user_ids[i]
              flight_id = random.choice(flight_ids)  # Get a random flight_id from the list

              baggage = Baggage(
                  flight_id=flight_id,
                  user_id=user_id,  # Link the user to the baggage
                  baggage_tag=f"BAGGAGE-{i+1:03d}",
                  status=random.choice(['checked-in', 'in-transit', 'delivered', 'lost']),
                  last_updated=datetime.utcnow()
              )
              baggages.append(baggage)

          db.session.add_all(baggages)
          db.session.commit()
          print("10 Baggage records added to the database linked to the existing users!")