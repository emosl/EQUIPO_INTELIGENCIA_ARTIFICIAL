from schemas import *
from services import *
import models

from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

import schemas
import services
import models

app = FastAPI()

create_database()

@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(
    user_in: schemas.UserCreate,
    db: Session = Depends(services.get_db),
):
    # 1) Check for existing email
    existing = services.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The entered email is already in use"
        )

    # 2) Call the service-layer function (not itself)
    created_user = services.create_user(db=db, user=user_in)
    return created_user

@app.post(
    "/users/{user_id}/patients",
    response_model=schemas.Patient)
def create_patient_for_user(
    user_id: int,
    patient_in: schemas.PatientCreate,
    db: Session = Depends(services.get_db),
):
    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )

    new_patient = services.create_patient(db, user_id, patient_in)
    return new_patient


@app.get(
    "/users/{user_id}/patients",
    response_model=List[sch.Patient],
    summary="Get all patients for a specific user",
)
def read_patients_for_user(
    user_id: int,
    db: Session = Depends(services.get_db)
):
    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    patients = services.get_patients_by_user(db, user_id)
    return patients