from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import secrets

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///contracts.db')

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Initialize the database, creating all tables."""
    try:
        # First create all tables from SQLAlchemy models
        Base.metadata.create_all(engine)
        
        # Then create additional tables not managed by SQLAlchemy
        metadata = MetaData()
        
        # Reflect existing tables
        metadata.reflect(bind=engine)
        
        # Define invitations table
        invitations = Table('invitations', metadata,
            Column('id', Integer, primary_key=True),
            Column('contract_id', String, ForeignKey('contracts.id')),
            Column('email', String, nullable=False),
            Column('role', String, nullable=False),
            Column('message', Text),
            Column('status', String, nullable=False),
            Column('token', String, nullable=False),
            Column('created_at', DateTime, nullable=False),
            Column('expires_at', DateTime, nullable=False),
            extend_existing=True
        )
        
        # Drop and recreate invitations table
        db = Session()
        try:
            # Drop existing table if it exists
            db.execute(text('DROP TABLE IF EXISTS invitations'))
            db.commit()
            
            # Create table with new schema
            invitations.create(engine)
            db.commit()
            print("Successfully initialized database and created all tables")
        except Exception as e:
            print(f"Error creating invitations table: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_db():
    """Get a new database session."""
    return Session()

def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)
