import io
import schemas
import services
import models
import pandas as pd, io



from typing import List
from loadenv import Settings
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

services.create_database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # used by FastAPI's dependency later

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

    existing = services.get_user_by_email(db, patient_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The entered email is already in use, please use another one"
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

# ADD THIS NEW ENDPOINT
@app.get("/users/me", response_model=schemas.User)
def get_current_user_endpoint(
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    """
    Get the current authenticated user's information.
    This endpoint is called by the React app after login to fetch user details.
    """
    return current_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(services.get_db),
):
    """
    Accepts form-encoded fields: `username` (our email) and `password`.
    If authentication succeeds, returns a JWT access_token.
    """
    # form_data.username is the "username" field in the OAuth2 form; we'll treat that as email
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
        data={"sub": user.email},  # we store email in the "sub" claim
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



class EegUploadMeta(BaseModel):
    session_id: int   # you can add more fields later

REQUIRED = [
    "af3","f7","f3","fc5","t7","p7",
    "o1","o2","p8","t8","fc6","f4","f8","af4"
]

@app.post("/upload/csv")
async def upload_csv(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user),
):
    raw = await file.read()

    # try reading with header first
    df = pd.read_csv(io.BytesIO(raw))

    # if the first column is numeric we probably have NO header
    if list(df.columns) == list(range(len(df.columns))):
        if len(df.columns) != 14:
            raise HTTPException(400, "CSV must have 14 EEG columns")
        df.columns = REQUIRED                      # slap the names on
    else:
        # normal case: check that all required names are present (case-insensitive)
        df.columns = df.columns.str.lower()
        if not set(REQUIRED).issubset(df.columns):
            raise HTTPException(400, "CSV missing EEG columns")

    rows = [
        models.EegData(session_id=session_id, **row[REQUIRED].astype(float))
        for _, row in df.iterrows()
    ]
    db.add_all(rows)
    db.commit()
    return {"inserted": len(rows)}

