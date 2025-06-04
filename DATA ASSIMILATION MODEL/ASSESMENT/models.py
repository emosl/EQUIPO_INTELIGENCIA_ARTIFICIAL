# models.py

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from database import Base  # ← must be the same Base that your database.py uses


# ── (your existing User, Patient, Session, EegData remain unchanged) ─────────

class User(Base):
    __tablename__ = "users"
    id                 = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    name               = Column(String(100), nullable=False)
    father_surname     = Column(String(100), nullable=False)
    mother_surname     = Column(String(100), nullable=False)
    medical_department = Column(String(100), nullable=False)
    email              = Column(String(254), unique=True, nullable=False)
    hashed_password    = Column(String(256), nullable=False)
    is_active          = Column(Boolean, default=True, nullable=False)

    patients = relationship("Patient", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"
    id             = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    name           = Column(String(100), nullable=False)
    father_surname = Column(String(100), nullable=False)
    mother_surname = Column(String(100), nullable=False)
    birth_date     = Column(Date, nullable=False)
    sex            = Column(String(1), nullable=False)
    email          = Column(String(254), unique=True, nullable=False)

    user     = relationship("User", back_populates="patients")
    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = "sessions"
    id                = Column(Integer, primary_key=True, index=True, nullable=False)
    patient_id        = Column(Integer, ForeignKey("patients.id"), nullable=False)
    session_timestamp = Column(DateTime, default=datetime.now(), nullable=False)
    flag              = Column(String, nullable=False)

    patient           = relationship("Patient", back_populates="sessions")
    eeg_data          = relationship("EegData", back_populates="session")

    # ← THESE MUST MATCH the new Results classes below:
    results_y         = relationship("ResultsY",    back_populates="session",    cascade="all, delete-orphan")
    results_amplitude = relationship("ResultsAmp",  back_populates="session",    cascade="all, delete-orphan")
    results_welch     = relationship("ResultsWelch", back_populates="session",    cascade="all, delete-orphan")


class EegData(Base):
    __tablename__ = "eeg_data"
    id         = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    af3        = Column(Float, nullable=False)
    f7         = Column(Float, nullable=False)
    f3         = Column(Float, nullable=False)
    fc5        = Column(Float, nullable=False)
    t7         = Column(Float, nullable=False)
    p7         = Column(Float, nullable=False)
    o1         = Column(Float, nullable=False)
    o2         = Column(Float, nullable=False)
    p8         = Column(Float, nullable=False)
    t8         = Column(Float, nullable=False)
    fc6        = Column(Float, nullable=False)
    f4         = Column(Float, nullable=False)
    f8         = Column(Float, nullable=False)
    af4        = Column(Float, nullable=False)

    session = relationship("Session", back_populates="eeg_data")


# ── Kalman “Algorithm” and “Results” tables ──────────────────────────────────

class Algorithm(Base):
    __tablename__ = "algorithm"
    id          = Column(Integer, primary_key=True, index=True, nullable=False)
    name        = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)

    # These back_populates must match below
    results_y     = relationship("ResultsY",    back_populates="algorithm", cascade="all, delete-orphan")
    results_amp   = relationship("ResultsAmp",  back_populates="algorithm", cascade="all, delete-orphan")
    results_welch = relationship("ResultsWelch", back_populates="algorithm", cascade="all, delete-orphan")


class ResultsY(Base):
    __tablename__ = "results_y"
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)

    # NEW column “label” to distinguish All / WC / NWC
    label        = Column(String(16), nullable=False)

    y_value      = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)

    session      = relationship("Session",   back_populates="results_y")
    algorithm    = relationship("Algorithm", back_populates="results_y")


class ResultsAmp(Base):
    __tablename__ = "results_amplitude"
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)

    # NEW column “label” to distinguish All / Original / WC / NWC
    label        = Column(String(16), nullable=False)

    amplitude    = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)

    session      = relationship("Session",   back_populates="results_amplitude")
    algorithm    = relationship("Algorithm", back_populates="results_amp")


class ResultsWelch(Base):
    __tablename__ = "results_welch"
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)

    # NEW: one row per frequency, storing all four PSD powers in the same row
    frequency      = Column(Float, nullable=False)
    power_all      = Column(Float, nullable=False)
    power_original = Column(Float, nullable=False)
    power_wc       = Column(Float, nullable=False)
    power_nwc      = Column(Float, nullable=False)

    session      = relationship("Session",   back_populates="results_welch")
    algorithm    = relationship("Algorithm", back_populates="results_welch")
