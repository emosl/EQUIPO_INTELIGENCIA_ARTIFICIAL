import models as mod
import schemas as sch
from database import *
from sqlalchemy.orm import *

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
    db_user = mod.User(name=user.name, father_surname=user.father_surname, mother_surname=user.mother_surname, medical_department=user.medical_department, email=user.email, password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
