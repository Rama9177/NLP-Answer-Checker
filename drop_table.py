from app import db
from models import UserResponse

# Drop the UserResponse table if it exists
UserResponse.__table__.drop(db.engine)

# Create all tables again
db.create_all()
