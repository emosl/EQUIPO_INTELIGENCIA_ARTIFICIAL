# main.py

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

# Import the updated models (make sure these match the modified models.py)
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

# Map variant‐string → run() function
kalman_variants: Dict[str, callable] = {
    "Potter_GramSchmidt":    kpgs.run,
    "Carlson_GramSchmidt":   kcgs.run,
    "Bierman_GramSchmidt":   kgbgs.run,
    "Potter_Givens":         kpgv.run,
    "Carlson_Givens":        kcg.run,
    "Bierman_Givens":        kgbgv.run,
    "Potter_Householder":    kphp.run,
    "Carlson_Householder":   khc.run,
    "Bierman_Householder":   khb.run,
}

Fs = 128
AMP_LABELS = ["All", "Original", "WC", "NWC"]

# MySQL FLOAT max (approx): ±3.4 × 10^38
MAX_FLOAT32 = 3.4e38

# ── Database dependency ─────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_algorithm(db: Session, variant_name: str) -> Algorithm:
    """Get existing algorithm or insert a new row if missing."""
    algo = db.query(Algorithm).filter(Algorithm.name == variant_name).first()
    if not algo:
        algo = Algorithm(
            name=variant_name,
            description=f"Kalman filter variant: {variant_name}"
        )
        db.add(algo)
        db.commit()
        db.refresh(algo)
    return algo

# ── Helpers to insert into each Results table ────────────────────────────────

def store_y_result(
    db: Session,
    session_id: int,
    algorithm_id: int,
    label: str,
    y_value: float,
    time_val: float,
) -> ResultsY:
    """Insert one row into results_y (with a label)."""
    row = ResultsY(
        session_id=session_id,
        algorithm_id=algorithm_id,
        label=label,
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
    label: str,
    amplitude: float,
    time_val: float,
) -> ResultsAmp:
    """Insert one row into results_amplitude (with a label)."""
    row = ResultsAmp(
        session_id=session_id,
        algorithm_id=algorithm_id,
        label=label,
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
    frequency: float,
    power_all: float,
    power_original: float,
    power_wc: float,
    power_nwc: float,
) -> ResultsWelch:
    """Insert one row into results_welch (one row per frequency, with all 4 power columns)."""
    row = ResultsWelch(
        session_id=session_id,
        algorithm_id=algorithm_id,
        frequency=frequency,
        power_all=power_all,
        power_original=power_original,
        power_wc=power_wc,
        power_nwc=power_nwc,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

# ────────────────────────────────────────────────────────────────────────────

@app.post("/run-kalman", response_model=RunResponse)
async def run_kalman_endpoint(
    variant: str = Form(...),
    wC: str = Form(...),
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1) Validate the requested Kalman variant
    if variant not in kalman_variants:
        raise HTTPException(400, f"Unknown variant '{variant}'")

    # 2) Parse wC (JSON‐encoded list of 14 integers)
    try:
        wC_arr = np.array(json.loads(wC), dtype=int)
        assert wC_arr.size == 14
    except Exception:
        raise HTTPException(400, "wC must be JSON list of 14 ints")

    # 3) Save the uploaded CSV into a temporary file
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "file must be a .csv")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    file.file.close()

    # 4) Verify that the given session exists
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")

    # 5) Find (or create) the Algorithm row so we know algorithm.id
    algorithm = get_or_create_algorithm(db, variant)

    # 6) Run the chosen Kalman variant → returns four amplitude arrays + three y arrays
    try:
        run_fn = kalman_variants[variant]
        amp_all, amp_orig, amp_wc, amp_nwc, y_all, y_wc, y_nwc = run_fn(
            tmp_path, Fs, wC_arr
        )
    except Exception as e:
        raise HTTPException(500, f"Kalman error: {e}")
    finally:
        os.unlink(tmp_path)  # always delete temp file

    # 7) Build four amplitude arrays and three y arrays (flatten + convert to float + replace NaN/Inf with zero)
    amps_raw = {
        "All":      np.nan_to_num(np.array(amp_all).ravel().astype(float)),
        "Original": np.nan_to_num(np.array(amp_orig).ravel().astype(float)),
        "WC":       np.nan_to_num(np.array(amp_wc).ravel().astype(float)),
        "NWC":      np.nan_to_num(np.array(amp_nwc).ravel().astype(float)),
    }

    ys_raw = {
        "All": np.nan_to_num(np.array(y_all).ravel().astype(float)),
        "WC":  np.nan_to_num(np.array(y_wc).ravel().astype(float)),
        "NWC": np.nan_to_num(np.array(y_nwc).ravel().astype(float)),
    }

    # 8) Compute Welch PSD for those four amplitude arrays
    try:
        freqs, psd = psd_from_arrays(amps_raw, fs=Fs, nperseg=Fs)
    except Exception as e:
        raise HTTPException(500, f"Welch error: {e}")

    freqs_clean = np.nan_to_num(np.array(freqs, dtype=float))
    psd_clean: Dict[str, np.ndarray] = {}
    for label in AMP_LABELS:
        psd_clean[label] = np.nan_to_num(np.array(psd[label], dtype=float))

    # 9) Insert **every** sample of the Y arrays into `results_y`
    #    We use time_val = sample index (0…, Nsamples−1) and label in {"All","WC","NWC"}.
    n_samples = len(ys_raw["All"])  # e.g. 3073
    for label, arr in ys_raw.items():
        for idx in range(n_samples):
            y_val = float(arr[idx])
            if not np.isfinite(y_val):
                y_val = 0.0
            if abs(y_val) > MAX_FLOAT32:
                y_val = float(np.sign(y_val) * MAX_FLOAT32)

            store_y_result(
                db=db,
                session_id=session_id,
                algorithm_id=algorithm.id,
                label=label,         # e.g. "All" or "WC" or "NWC"
                y_value=y_val,
                time_val=float(idx), # sample‐index
            )

    # 10) Insert **every** sample of the amplitude arrays into `results_amplitude`
    #     We use time_val = sample index (0…, Nsamples−1) and label in {"All","Original","WC","NWC"}.
    for label, arr in amps_raw.items():
        for idx in range(n_samples):
            amp_val = float(arr[idx])
            if not np.isfinite(amp_val):
                amp_val = 0.0
            if abs(amp_val) > MAX_FLOAT32:
                amp_val = float(np.sign(amp_val) * MAX_FLOAT32)

            store_amp_result(
                db=db,
                session_id=session_id,
                algorithm_id=algorithm.id,
                label=label,         # "All", "Original", "WC", or "NWC"
                amplitude=amp_val,
                time_val=float(idx),
            )

    # 11) Insert **one row per frequency** into `results_welch`
    #      Each row holds (frequency, power_all, power_original, power_wc, power_nwc).
    n_bins = len(freqs_clean)  # e.g. 65 if nperseg=128
    for bin_idx in range(n_bins):
        freq_val = float(freqs_clean[bin_idx])

        # Extract each label’s PSD at this frequency bin
        p_all  = float(psd_clean["All"][bin_idx])
        p_orig = float(psd_clean["Original"][bin_idx])
        p_wc   = float(psd_clean["WC"][bin_idx])
        p_nwc  = float(psd_clean["NWC"][bin_idx])

        # Replace NaN or ±Inf → 0.0, then clip to ±MAX_FLOAT32
        def clamp(val):
            if not np.isfinite(val):
                val = 0.0
            if abs(val) > MAX_FLOAT32:
                val = float(np.sign(val) * MAX_FLOAT32)
            return val

        store_welch_result(
            db=db,
            session_id=session_id,
            algorithm_id=algorithm.id,
            frequency=freq_val,
            power_all = clamp(p_all),
            power_original = clamp(p_orig),
            power_wc  = clamp(p_wc),
            power_nwc = clamp(p_nwc),
        )

    # 12) Finally, return a JSON‐body containing all raw time‐series so the client can plot if desired:
    return RunResponse(
        y_all=ys_raw["All"].tolist(),
        y_winningcomb=ys_raw["WC"].tolist(),
        y_nonwinning=ys_raw["NWC"].tolist(),

        amplitude_all=amps_raw["All"].tolist(),
        amplitude_winning=amps_raw["WC"].tolist(),
        amplitude_nonwinning=amps_raw["NWC"].tolist(),
        amplitude_original=amps_raw["Original"].tolist(),

        welch={
            "frequencies": freqs_clean.tolist(),
            "power": { lab: psd_clean[lab].tolist() for lab in AMP_LABELS },
        },
    )

# ────────────────────────────────────────────────────────────────────────────

@app.get("/results/{session_id}")
async def get_session_results(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetch back all of the “Y” rows (which are Nsamples * 3 rows).
    (You can similarly add endpoints to fetch amplitude or welch rows if you want.)
    """
    rows = (
        db.query(ResultsY)
        .filter(ResultsY.session_id == session_id)
        .order_by(ResultsY.time.asc())
        .all()
    )
    if not rows:
        raise HTTPException(404, f"No Y‐values found for session {session_id}")

    return {
        "session_id": session_id,
        "results_y": [
            {
                "id":             r.id,
                "algorithm_id":   r.algorithm_id,
                "label":          r.label,
                "y_value":        float(r.y_value),
                "time":           float(r.time),
                "algorithm_name": (r.algorithm.name if r.algorithm else None),
            }
            for r in rows
        ],
    }
