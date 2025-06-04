# database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DEFAULT_URL = "mysql+pymysql://app_user:app_pass@127.0.0.1:3306/datamed?charset=utf8mb4"
SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL", DEFAULT_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ── Import all models so that SQLAlchemy sees them before create_all() ─────────
from models import (
    Algorithm,
    Session as SessionModel,
    ResultsY,
    ResultsAmp,
    ResultsWelch,
)

# ── Create any missing tables in the database ────────────────────────────────
Base.metadata.create_all(bind=engine)
