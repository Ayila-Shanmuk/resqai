"""
Database connection and session management.

Uses SQLite for local development. The code is written against SQLAlchemy's
engine/session abstraction only, so switching to MySQL/PostgreSQL later is a
one-line change to DATABASE_URL (plus adding the driver to requirements.txt) -
no other code in this project needs to change.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example for future migration:
#   PostgreSQL: postgresql://user:password@localhost:5432/resqai
#   MySQL:      mysql+pymysql://user:password@localhost:3306/resqai
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resqai.db")

# Render and Heroku sometimes provide 'postgres://' which SQLAlchemy 2.0 requires as 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on backend startup."""
    from models import database_models  # noqa: F401  (registers tables on Base)
    Base.metadata.create_all(bind=engine)
