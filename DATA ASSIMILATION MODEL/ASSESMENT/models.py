# models.py

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Algorithm(Base):
    __tablename__ = "algorithm"
    
    id          = Column(Integer, primary_key=True, index=True, nullable=False)
    name        = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)

    # ← add these three lines:
    results_y     = relationship("ResultsY",    back_populates="algorithm", cascade="all, delete-orphan")
    results_amp   = relationship("ResultsAmp",  back_populates="algorithm", cascade="all, delete-orphan")
    results_welch = relationship("ResultsWelch", back_populates="algorithm", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    
    id                = Column(Integer, primary_key=True, index=True, nullable=False)
    patient_id        = Column(Integer, ForeignKey("patients.id"), nullable=False)
    session_timestamp = Column(DateTime, default=datetime.now(), nullable=False)

    # ← add these three lines:
    results_y     = relationship("ResultsY",    back_populates="session",    cascade="all, delete-orphan")
    results_amp   = relationship("ResultsAmp",  back_populates="session",    cascade="all, delete-orphan")
    results_welch = relationship("ResultsWelch", back_populates="session",    cascade="all, delete-orphan")


class ResultsY(Base):
    __tablename__ = "results_y"
    
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)
    y_value      = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)
    
    session   = relationship("Session",   back_populates="results_y")
    algorithm = relationship("Algorithm", back_populates="results_y")


class ResultsAmp(Base):
    __tablename__ = "results_amp"
    
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)
    amplitude    = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)
    
    session   = relationship("Session",   back_populates="results_amp")
    algorithm = relationship("Algorithm", back_populates="results_amp")


class ResultsWelch(Base):
    __tablename__ = "results_welch"
    
    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)
    y_value      = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)
    
    session   = relationship("Session",   back_populates="results_welch")
    algorithm = relationship("Algorithm", back_populates="results_welch")
