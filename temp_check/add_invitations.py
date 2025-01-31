from sqlalchemy import create_engine
from models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database engine
engine = create_engine('sqlite:///contracts.db')

def upgrade():
    # Create all tables
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    upgrade()
    print("Database migration completed successfully!")
