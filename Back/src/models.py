import datetime as dt
import database as database
import sqlalchemy.orm as orm

from sqlalchemy import Boolean, Column, Date, DateTime, Double, ForeignKey, Integer, String

class User(database.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    father_surname = Column(String)
    mother_surname = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, Full Name={self.name} {self.father_surname} {self.mother_surname}, email={self.email}, is_active={self.is_active})>"

class Patient(database.Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    father_surname = Column(String)
    mother_surname = Column(String)
    birth_date = Column(Date)
    sex = Column(String)

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, Full Name={self.name} {self.father_surname} {self.mother_surname}, birth_date={self.birth_date}, sex={self.sex})>"

class Session(database.Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    session_timestamp = Column(DateTime, default=dt.datetime.now())
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, patient_id={self.patient_id}, user_id={self.user_id}, session_timestamp={self.session_timestamp})>"

class EegData(database.Base):
    __tablename__ = "eeg_data"
    session_id = Column(Integer, ForeignKey("sessions.id"))
    af3 = Column(Double)
    f7 = Column(Double)
    f3 = Column(Double)
    fc5 = Column(Double)
    t7 = Column(Double)
    p7 = Column(Double)
    o1 = Column(Double)
    o2 = Column(Double)
    p8 = Column(Double)
    t8 = Column(Double)
    fc6 = Column(Double)
    f4 = Column(Double)
    f8 = Column(Double)
    af4 = Column(Double)

    def __repr__(self) -> str:
        return f"<EEGData(id={self.session_id}, af3={self.af3}, f7={self.f7}, f3={self.f3}, fc5={self.fc5}, t7={self.t7}, p7={self.p7}, o1={self.o1}, o2={self.o2}, p8={self.p8}, t8={self.t8}, fc6={self.fc6}, f4={self.f4}, f8={self.f8}, af4={self.af4})>"
    
def main() -> None:
    return