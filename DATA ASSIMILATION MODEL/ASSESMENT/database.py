# database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# (1) Connection URL
DEFAULT_URL = "mysql+pymysql://app_user:app_pass@127.0.0.1:3306/datamed?charset=utf8mb4"
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", DEFAULT_URL)

# (2) Engine & SessionLocal
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# (3) The shared “Base” for all ORM classes
Base = declarative_base()

# (4) Import your ORM classes so that they register with Base
from models import (
    User,
    Patient,
    Session as SessionModel,
    EegData,
    Algorithm,
    ResultsY,
    ResultsAmp,
    ResultsWelch,
)

# (5) Create all tables that don’t exist yet
Base.metadata.create_all(bind=engine)
