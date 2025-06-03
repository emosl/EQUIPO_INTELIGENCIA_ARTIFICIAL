import schemas
import services
import models

from typing import List
from loadenv import Settings
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
services.create_database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # used by FastAPI’s dependency later

@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(
    user_in: schemas.UserCreate,
    db: Session = Depends(services.get_db),
):
    existing = services.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The entered email is already in use"
        )
    created_user = services.create_user(db=db, user=user_in)
    return created_user

@app.post("/users/{user_id}/patients", response_model=schemas.Patient)
def create_patient_for_user(
    user_id: int,
    patient_in: schemas.PatientCreate,
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )

    new_patient = services.create_patient(db, user_id, patient_in)
    return new_patient


@app.get("/users/{user_id}/patients", response_model=List[schemas.Patient], summary="Get all patients for a specific user")
def read_patients_for_user(
    user_id: int,
    db: Session = Depends(services.get_db)
):
    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    patients = services.get_patients_by_user(db, user_id)
    return patients

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(services.get_db),
):
    """
    Accepts form-encoded fields: `username` (our email) and `password`.
    If authentication succeeds, returns a JWT access_token.
    """
    # form_data.username is the “username” field in the OAuth2 form; we’ll treat that as email
    user = services.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a token that expires in ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=services.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.create_access_token(
        data={"sub": user.email},  # we store email in the “sub” claim
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}