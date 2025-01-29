"""Initial data

Revision ID: 6cb15a659d4d
Revises: 97f3b2b73a2d
Create Date: 2025-01-29 19:15:11.980790

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from werkzeug.security import generate_password_hash
from app.models import User, ParkingSpot


# revision identifiers, used by Alembic.
revision = '4577fb96bf4f'
down_revision = '97f3b2b73a2d'
branch_labels = None
depends_on = None

def seed_data():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # Create an admin user
    admin_user = User(username="Amine maaloul", email="Aminemaaloul@gmail.com.com", password=generate_password_hash("Amine123"), role="admin")
    session.add(admin_user)

    # Create some regular users
    user1 = User(username="Becher zribi", email="becherzribi@gmail.com", password=generate_password_hash("Becher123"))
    user2 = User(username="ahmed louati", email="ahmedlouati@gmail.com", password=generate_password_hash("Ahmed123"))
    session.add(user1)
    session.add(user2)
   
    # Create Parking Spots
    spot1 = ParkingSpot(location="A1")
    spot2 = ParkingSpot(location="B2")
    spot3 = ParkingSpot(location="C3")
    session.add(spot1)
    session.add(spot2)
    session.add(spot3)

    session.commit()

def upgrade():
    seed_data()

def downgrade():
    pass

