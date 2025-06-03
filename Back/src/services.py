import models as mod
import schemas as sch
from database import *
from sqlalchemy.orm import *
from typing import List

def create_database():
    return Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: Session, email: str):
    return db.query(mod.User).filter(mod.User.email == email).first()

def create_user(db: Session, user: sch.UserCreate):
    hashed_pass = user.password + "thisisnotsecure"
    db_user = mod.User(name=user.name, father_surname=user.father_surname, mother_surname=user.mother_surname, medical_department=user.medical_department, email=user.email, hashed_password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_patients_by_user(db: Session, user_id: int) -> List[mod.Patient]:
    return db.query(mod.Patient).filter(mod.Patient.user_id == user_id).all()

def create_patient(db: Session, user_id: int, patient_in: sch.PatientCreate) -> mod.Patient:
    new_patient = mod.Patient(
        user_id=user_id,
        name=patient_in.name,
        father_surname=patient_in.father_surname,
        mother_surname=patient_in.mother_surname,
        birth_date=patient_in.birth_date,
        sex=patient_in.sex
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient