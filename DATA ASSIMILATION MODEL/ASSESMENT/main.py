import os
import json
import shutil
import tempfile
from typing import Dict

import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from schemas import RunResponse
from Welch import psd_from_arrays
from database import SessionLocal

# Import your models (make sure these exist in models.py and that you have created their tables)
from models import (
    ResultsY,
    ResultsAmp,
    ResultsWelch,
    Algorithm,
    Session as SessionModel,
)

# ── Kalman variant imports ───────────────────────────────────────────────────
import Kalman_GramShmidt_Potter    as kpgs
import Kalman_GramShmidt_Carlson   as kcgs
import Kalman_GramShmidt_Bierman   as kgbgs
import Kalman_Givens_Potter        as kpgv
import Kalman_Givens_Carlson       as kcg
import Kalman_Givens_Bierman       as kgbgv
import Kalman_Householder_Potter   as kphp
import Kalman_Householder_Carlson  as khc
import Kalman_Householder_Bierman  as khb

app = FastAPI()

# Map variant-string → run() function
kalman_variants: Dict[str, callable] = {
    'Potter_GramSchmidt':    kpgs.run,
    'Carlson_GramSchmidt':   kcgs.run,
    'Bierman_GramSchmidt':   kgbgs.run,
    'Potter_Givens':         kpgv.run,
    'Carlson_Givens':        kcg.run,
    'Bierman_Givens':        kgbgv.run,
    'Potter_Householder':    kphp.run,
    'Carlson_Householder':   khc.run,
    'Bierman_Householder':   khb.run,
}

Fs = 128
AMP_LABELS = ["All", "Original", "WC", "NWC"]
# Maximum magnitude for MySQL FLOAT (~3.4e38)
MAX_FLOAT32 = 3.4e38

# ── Database dependency ───────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_algorithm(db: Session, variant_name: str) -> Algorithm:
    """Get existing algorithm or create new one"""
    algorithm = db.query(Algorithm).filter(Algorithm.name == variant_name).first()
    if not algorithm:
        algorithm = Algorithm(
            name=variant_name,
            description=f"Kalman filter variant: {variant_name}"
        )
        db.add(algorithm)
        db.commit()
        db.refresh(algorithm)
    return algorithm

# ── Helper functions to store into separate result tables ────────────────────
def store_y_result(
    db: Session,
    session_id: int,
    algorithm_id: int,
    y_value: float,
    time_val: float,
) -> ResultsY:
    """Insert one row into ResultsY."""
    row = ResultsY(
        session_id=session_id,
        algorithm_id=algorithm_id,
        y_value=y_value,
        time=time_val,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def store_amp_result(
    db: Session,
    session_id: int,
    algorithm_id: int,
    amplitude: float,
    time_val: float,
) -> ResultsAmp:
    """Insert one row into ResultsAmp."""
    row = ResultsAmp(
        session_id=session_id,
        algorithm_id=algorithm_id,
        amplitude=amplitude,
        time=time_val,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def store_welch_result(
    db: Session,
    session_id: int,
    algorithm_id: int,
    y_value: float,
    time_val: float,
) -> ResultsWelch:
    """Insert one row into ResultsWelch."""
    row = ResultsWelch(
        session_id=session_id,
        algorithm_id=algorithm_id,
        y_value=y_value,
        time=time_val,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

# ───────────────────────────────────────────────────────────────────────────
@app.post("/run-kalman", response_model=RunResponse)
async def run_kalman_endpoint(
    variant: str = Form(...),
    wC: str = Form(...),
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1) variant check
    if variant not in kalman_variants:
        raise HTTPException(400, f"Unknown variant '{variant}'")

    # 2) parse wC
    try:
        wC_arr = np.array(json.loads(wC), dtype=int)
        assert wC_arr.size == 14
    except Exception:
        raise HTTPException(400, "wC must be JSON list of 14 ints")

    # 3) save CSV to temp file
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "file must be .csv")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    file.file.close()

    # 4) Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")

    # 5) Get or create algorithm
    algorithm = get_or_create_algorithm(db, variant)

    # 6) run Kalman
    try:
        run_fn = kalman_variants[variant]
        amp_all, amp_orig, amp_wc, amp_nwc, y_all, y_wc, y_nwc = run_fn(
            tmp_path, Fs, wC_arr
        )
    except Exception as e:
        raise HTTPException(500, f"Kalman error: {e}")
    finally:
        os.unlink(tmp_path)

    # 7) Welch PSDs
    amps_raw = {
        "All":      np.nan_to_num(np.array(amp_all).ravel()),
        "Original": np.nan_to_num(np.array(amp_orig).ravel()),
        "WC":       np.nan_to_num(np.array(amp_wc).ravel()),
        "NWC":      np.nan_to_num(np.array(amp_nwc).ravel()),
    }
    try:
        freqs, psd = psd_from_arrays(amps_raw, fs=Fs, nperseg=Fs)
    except Exception as e:
        raise HTTPException(500, f"Welch error: {e}")

    # Clean NaN / ±Inf in freqs and PSD arrays
    freqs_clean = np.nan_to_num(np.array(freqs))
    psd_clean: Dict[str, np.ndarray] = {}
    for label in AMP_LABELS:
        psd_clean[label] = np.nan_to_num(np.array(psd[label]))

    # 8) Calculate summary statistics

    # Clean amplitude arrays by clipping to reasonable bounds before calculating means
    def clip_and_mean(arr):
        """Clip array values to MySQL FLOAT range and calculate mean"""
        clipped = np.clip(arr, -MAX_FLOAT32, MAX_FLOAT32)
        return float(np.mean(clipped))

    # Amplitude means (clipped to prevent overflow)
    amp_all_summary  = clip_and_mean(amps_raw["All"])
    amp_orig_summary = clip_and_mean(amps_raw["Original"])
    amp_wc_summary   = clip_and_mean(amps_raw["WC"])
    amp_nwc_summary  = clip_and_mean(amps_raw["NWC"])

    # Y‐values: force to scalar float (take mean if array)
    def to_scalar(x):
        arr = np.array(x).astype(float)
        # Clip to MySQL FLOAT range
        arr = np.clip(arr, -MAX_FLOAT32, MAX_FLOAT32)
        arr = np.nan_to_num(arr)
        return float(np.mean(arr)) if arr.size > 1 else float(arr)

    y_all_scalar  = to_scalar(y_all)
    y_wc_scalar   = to_scalar(y_wc)
    y_nwc_scalar  = to_scalar(y_nwc)

    # Log warnings about extreme values
    for name, arr in amps_raw.items():
        max_val = np.max(np.abs(arr))
        if max_val > MAX_FLOAT32:
            print(f"Warning: {name} array contains values exceeding MySQL FLOAT range (max: {max_val:.2e})")

    # Welch summary: mean of all PSD label means (with clipping)
    welch_summary = float(np.mean([np.clip(psd_clean[label], -MAX_FLOAT32, MAX_FLOAT32).mean() for label in AMP_LABELS]))

    # ── Store into the separate "Results" tables (with overflow checks) ────────
    try:
        # a) Store Y‐values as three rows
        y_values = [
            ("y_all", y_all_scalar),
            ("y_wc", y_wc_scalar),
            ("y_nwc", y_nwc_scalar)
        ]
        
        for label, val in y_values:
            if np.isfinite(val) and abs(val) <= MAX_FLOAT32:
                _ = store_y_result(
                    db=db,
                    session_id=session_id,
                    algorithm_id=algorithm.id,
                    y_value=val,
                    time_val=val,
                )
            else:
                print(f"Warning: Skipping {label} insert (value: {val:.2e})")

        # b) Store four amplitude summaries
        amp_summaries = [
            ("amp_all", amp_all_summary),
            ("amp_orig", amp_orig_summary),
            ("amp_wc", amp_wc_summary),
            ("amp_nwc", amp_nwc_summary)
        ]
        
        for label, amp_summary in amp_summaries:
            if np.isfinite(amp_summary) and abs(amp_summary) <= MAX_FLOAT32:
                _ = store_amp_result(
                    db=db,
                    session_id=session_id,
                    algorithm_id=algorithm.id,
                    amplitude=amp_summary,
                    time_val=amp_summary,
                )
            else:
                print(f"Warning: Skipping {label} insert (value: {amp_summary:.2e})")

        # c) Store one Welch summary row
        if np.isfinite(welch_summary) and abs(welch_summary) <= MAX_FLOAT32:
            _ = store_welch_result(
                db=db,
                session_id=session_id,
                algorithm_id=algorithm.id,
                y_value=welch_summary,
                time_val=welch_summary,
            )
        else:
            print(f"Warning: Skipping Welch insert (value: {welch_summary:.2e})")

    except Exception as e:
        # Log but don't fail the request
        print(f"Error storing results: {e}")
        db.rollback()

    # 9) respond with full data
    return RunResponse(
        # Return raw time‐series as lists (all NaN/Inf cleaned)
        y_all         = amps_raw["All"].tolist(),
        y_winningcomb = amps_raw["WC"].tolist(),
        y_nonwinning  = amps_raw["NWC"].tolist(),

        amplitude_all        = amps_raw["All"].tolist(),
        amplitude_winning    = amps_raw["WC"].tolist(),
        amplitude_nonwinning = amps_raw["NWC"].tolist(),
        amplitude_original   = amps_raw["Original"].tolist(),

        welch = {
            "frequencies": freqs_clean.tolist(),
            "power":       {lab: psd_clean[lab].tolist() for lab in AMP_LABELS},
        },
    )

# ───────────────────────────────────────────────────────────────────────────
@app.get("/results/{session_id}")
async def get_session_results(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get all Y‐value results for a specific session"""
    results = db.query(ResultsY).filter(ResultsY.session_id == session_id).all()
    if not results:
        raise HTTPException(404, f"No Y‐values found for session {session_id}")

    return {
        "session_id": session_id,
        "results_y": [
            {
                "id":             r.id,
                "algorithm_id":   r.algorithm_id,
                "y_value":        float(r.y_value),
                "time":           float(r.time),
                "algorithm_name": (r.algorithm.name if r.algorithm else None),
            }
            for r in results
        ],
    }