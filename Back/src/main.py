# backend_main.py

import io
import schemas
import services
import models
import pandas as pd, io
import requests
import json
import tempfile
import csv
import os
import time

from typing import List
from loadenv import Settings
from datetime import timedelta, datetime
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


@app.get("/sessions")
def get_sessions_for_user(
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    """
    Get all sessions for the current authenticated user.
    Returns sessions from all patients belonging to this user.
    """
    # 1) Gather all Session rows for this user
    sessions = (
        db.query(models.Session)
        .join(models.Patient)
        .filter(models.Patient.user_id == current_user.id)
        .all()
    )

    formatted_sessions = []
    for session in sessions:
        # Count EEG data points for this session to calculate size
        eeg_count = db.query(models.EegData).filter(
            models.EegData.session_id == session.id
        ).count()

        size_bytes = eeg_count * 14 * 8
        if size_bytes < 1024:
            size = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size = f"{size_bytes // 1024} KB"
        else:
            size = f"{size_bytes // (1024 * 1024)} MB"

        formatted_session = {
            "id": str(session.id),
            "name": f"Session {session.id} - {session.patient.name} {session.patient.father_surname}",
            "description": f"EEG session for patient {session.patient.name}, recorded on {session.session_timestamp.strftime('%Y-%m-%d')}",
            "size": size,
            "lastUpdated": session.session_timestamp.strftime('%Y-%m-%d %H:%M'),
             "algorithm_name": session.algorithm_name or "",        
            "processing_time": float(session.processing_time or 0.0)
        }
        formatted_sessions.append(formatted_session)
    return formatted_sessions


@app.post("/create-session-for-patient")
def create_session_for_patient(
    request: dict,  # {"patient_id": 123, "session_name": "..."}
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    """
    Create a new session for an existing patient
    """
    patient_id = request["patient_id"]
    session_name = request.get("session_name", f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Verify the patient belongs to the current user
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found or doesn't belong to current user"
        )
    
    # Create the session
    session = models.Session(
        patient_id=patient.id,
        session_timestamp=datetime.now(),
        flag=session_name
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"session_id": session.id, "patient_id": patient.id}

@app.post("/trigger-kalman-analysis")
async def trigger_kalman_analysis(
    request: dict,  # Now includes "models" list and "winning_combination"
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    session_id = request["session_id"]
    patient_id = request["patient_id"]
    models_list = request["models"]
    
    # GET THE USER-PROVIDED WINNING COMBINATION
    winning_combination = request.get(
        "winning_combination",
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0]
    )
    
    print(f"🔍 Starting analysis for session {session_id}")
    print(f"🧠 Models: {models_list}")
    print(f"⚡ User winning combination: {winning_combination}")
    
    # 1. Verify session belongs to current user
    session = db.query(models.Session).join(models.Patient).filter(
        models.Session.id == session_id,
        models.Patient.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(404, "Session not found or access denied")
    
    # 2. Get EEG data for this session
    eeg_data = db.query(models.EegData).filter(
        models.EegData.session_id == session_id
    ).all()
    
    if not eeg_data:
        raise HTTPException(404, "No EEG data found for this session")
    
    print(f"📊 Found {len(eeg_data)} EEG data points")
    
    # 3. Create temporary CSV file with EEG data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
        csv_writer = csv.writer(tmp_file)
        
        # Write header
        csv_writer.writerow([
            'af3', 'f7', 'f3', 'fc5', 't7', 'p7', 'o1', 'o2',
            'p8', 't8', 'fc6', 'f4', 'f8', 'af4'
        ])
        
        # Write data rows
        for eeg in eeg_data:
            csv_writer.writerow([
                eeg.af3, eeg.f7, eeg.f3, eeg.fc5, eeg.t7, eeg.p7, eeg.o1, eeg.o2,
                eeg.p8, eeg.t8, eeg.fc6, eeg.f4, eeg.f8, eeg.af4
            ])
        
        tmp_csv_path = tmp_file.name
    
    print(f"📁 Created CSV file: {tmp_csv_path} ({os.path.getsize(tmp_csv_path)} bytes)")
    try:
        results = []
        successful_runs = 0
        
        for model_name in models_list:
            print(f"🧠 Running model: {model_name}")
            try:
                kalman_api_url = "http://localhost:8001/run-kalman"
                
                request_data = {
                    "variant": model_name,
                    "wC": json.dumps(winning_combination),
                    "session_id": session_id
                }
                print(f"📤 Request data: {request_data}")
                
                with open(tmp_csv_path, 'rb') as csv_file:
                    print(f"📤 Sending request to Kalman API...")
                    start_time = time.time()
                    
                    response = requests.post(
                        kalman_api_url,
                        data=request_data,
                        files={"file": csv_file},
                        timeout=600
                    )
                    end_time = time.time()
                    processing_time = end_time - start_time
                    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
                
                print(f"📥 Kalman API response: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        # Now includes "session_run_id"
                        run_id = response_data.get("session_run_id")
                        print(f"✅ Model {model_name} completed successfully in {processing_time:.2f}s (new run: {run_id})")
                        successful_runs += 1
                        results.append({
                            "model": model_name,
                            "status": "success",
                            "session_run_id": run_id,
                            "processing_time": processing_time,
                            "data": response_data
                        })
                    except json.JSONDecodeError as e:
                        print(f"❌ Model {model_name} - Invalid JSON response: {e}")
                        results.append({
                            "model": model_name,
                            "status": "failed",
                            "error": f"Invalid JSON response: {e}",
                            "processing_time": processing_time
                        })
                else:
                    # HTTP error from Kalman service
                    error_text = response.text
                    print(f"❌ Model {model_name} failed with status {response.status_code}")
                    print(f"📝 Error details: {error_text}")
                    results.append({
                        "model": model_name,
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {error_text}",
                        "processing_time": processing_time
                    })
                    
            except Exception as e:
                print(f"💥 Exception for model {model_name}: {str(e)}")
                results.append({
                    "model": model_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        print(f"🏁 Analysis complete: {successful_runs}/{len(models_list)} successful")
        return {
            "message": f"Analysis completed for {successful_runs} out of {len(models_list)} models",
            "session_id": session_id,
            "patient_id": patient_id,
            "total_models": len(models_list),
            "successful_runs": successful_runs,
            "results": results
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_csv_path):
            os.unlink(tmp_csv_path)
            print(f"🗑️ Cleaned up CSV file")


@app.get("/sessions/{session_id}/results")
def get_session_results(
    session_id: int,
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(services.get_current_user)
):
    """Get analysis results for a session"""
    
    # Verify session belongs to user
    session = db.query(models.Session).join(models.Patient).filter(
        models.Session.id == session_id,
        models.Patient.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(404, "Session not found")
    
    # Get results (assuming you have a ResData table to store aggregated results)
    results = db.query(models.ResData).filter(
        models.ResData.session_id == session_id
    ).all()
    
    return {
        "session_id": session_id,
        "results": [
            {
                "id": r.id,
                "algorithm": r.algorithm.name if r.algorithm else "Unknown",
                "amplitude": r.amplitude,
                "welch": r.welch,
                "y_all": r.time,
                "y_wc": r.wilcoxon,
            }
            for r in results
        ]
    }
