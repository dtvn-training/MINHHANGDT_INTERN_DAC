"""This file manages the connection to the database. 
It contains the logic related to connection initiation 
and session management with SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from logics.config import Config

Base = declarative_base()
engine = engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """init database"""
    Base.metadata.create_all(bind=engine)
    