import os
import models
import schemas

from database import *
from loadenv import Settings
from sqlalchemy.orm import *
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_database():
    return Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pass = get_password_hash(user.password)
    db_user = models.User(name=user.name, father_surname=user.father_surname, mother_surname=user.mother_surname, medical_department=user.medical_department, email=user.email, hashed_password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_patients_by_user(db: Session, user_id: int) -> List[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).all()

def create_patient(db: Session, user_id: int, patient_in: schemas.PatientCreate) -> models.Patient:
    new_patient = models.Patient(
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

def get_password_hash(plain_password: str) -> str:
    """
    Hashes `plain_password` with bcrypt and returns the hash string.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Returns True if `plain_password` matches the `hashed_password`.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT token containing `data` (normally {"sub": <username_or_id>}) 
    that expires in `expires_delta`.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """
    Verify that a user with `email` exists and that `password` matches
    their stored hashed_password. Return the User object on success, or None.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Decode the JWT, find the user by email, and return the ORM user object.
    Raise 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user