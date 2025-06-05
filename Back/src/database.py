from loadenv import Settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"check_same_thread":False})

settings = Settings()

# NEW (for MySQL)
engine = create_engine(
    settings.DATABASE_URI,
    echo=True,        
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()