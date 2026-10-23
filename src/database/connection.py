
import os

import psycopg
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

load_dotenv()


def get_db_connection():
    """Create and return a PostgreSQL connection for database operations."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=10,
    )


def get_sqlalchemy_engine():
    """Create a SQLAlchemy engine for pandas database queries."""
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(
        database_url,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
    )
