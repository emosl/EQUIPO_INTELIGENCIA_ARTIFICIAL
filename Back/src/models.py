# models.py

from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    name               = Column(String(100), nullable=False)
    father_surname     = Column(String(100), nullable=False)
    mother_surname     = Column(String(100), nullable=False)
    medical_department = Column(String(100), nullable=False)
    email              = Column(String(254), unique=True, nullable=False)
    hashed_password    = Column(String(256), nullable=False)
    is_active          = Column(Boolean, default=True, nullable=False)

    patients = relationship("Patient", back_populates="user")

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, Full Name={self.name} "
            f"{self.father_surname} {self.mother_surname}, "
            f"MD={self.medical_department}, email={self.email}, "
            f"is_active={self.is_active})>"
        )


class Patient(Base):
    __tablename__ = "patients"

    id             = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    name           = Column(String(100), nullable=False)
    father_surname = Column(String(100), nullable=False)
    mother_surname = Column(String(100), nullable=False)
    birth_date     = Column(Date, nullable=False)
    sex            = Column(String(1), nullable=False)

    user     = relationship("User", back_populates="patients")
    sessions = relationship("Session", back_populates="patient")

    def __repr__(self) -> str:
        return (
            f"<Patient(id={self.id}, Full Name={self.name} "
            f"{self.father_surname} {self.mother_surname}, "
            f"birth_date={self.birth_date}, sex={self.sex})>"
        )


class Session(Base):
    __tablename__ = "sessions"

    id                = Column(Integer, primary_key=True, index=True, nullable=False)
    patient_id        = Column(Integer, ForeignKey("patients.id"), nullable=False)
    session_timestamp = Column(DateTime, default=datetime.now(), nullable=False)

    patient  = relationship("Patient", back_populates="sessions")
    eeg_data = relationship("EegData", back_populates="session")
    res_data = relationship("ResData", back_populates="session")

    def __repr__(self) -> str:
        return (
            f"<Session(id={self.id}, patient_id={self.patient_id}, "
            f"session_timestamp={self.session_timestamp})>"
        )


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

    def __repr__(self) -> str:
        return (
            f"<EegData(id={self.id}, session_id={self.session_id}, "
            f"af3={self.af3}, f7={self.f7}, f3={self.f3}, fc5={self.fc5}, "
            f"t7={self.t7}, p7={self.p7}, o1={self.o1}, o2={self.o2}, "
            f"p8={self.p8}, t8={self.t8}, fc6={self.fc6}, f4={self.f4}, "
            f"f8={self.f8}, af4={self.af4})>"
        )


class ResData(Base):
    __tablename__ = "res_data"

    id           = Column(Integer, primary_key=True, index=True, nullable=False)
    session_id   = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    amplitude    = Column(Float, nullable=False)
    welch        = Column(Float, nullable=False)
    time         = Column(Float, nullable=False)  # same type as welch
    wilcoxon     = Column(Float, nullable=False)  # same type as welch
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)

    session   = relationship("Session", back_populates="res_data")
    algorithm = relationship("Algorithm")

    def __repr__(self) -> str:
        return (
            f"<ResData(id={self.id}, session_id={self.session_id}, "
            f"amplitude={self.amplitude}, welch={self.welch}, "
            f"time={self.time}, wilcoxon={self.wilcoxon}, "
            f"algorithm_id={self.algorithm_id})>"
        )


class Algorithm(Base):
    __tablename__ = "algorithm"

    id          = Column(Integer, primary_key=True, index=True, nullable=False)
    name        = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Algorithm(id={self.id}, name={self.name}, "
            f"description={self.description})>"
        )

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}  # Add this line

    id                = Column(Integer, primary_key=True, index=True, nullable=False)
    patient_id        = Column(Integer, ForeignKey("patients.id"), nullable=False)
    session_timestamp = Column(DateTime, default=datetime.now(), nullable=False)

    patient  = relationship("Patient", back_populates="sessions")
    eeg_data = relationship("EegData", back_populates="session")
    res_data = relationship("ResData", back_populates="session")

    def __repr__(self) -> str:
        return (
            f"<Session(id={self.id}, patient_id={self.patient_id}, "
            f"session_timestamp={self.session_timestamp})>"
        )