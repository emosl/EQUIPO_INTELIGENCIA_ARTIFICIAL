# main.py 8001

import os
import json
import shutil
import tempfile
from typing import Dict

import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from schemas import RunResponse
from Welch import psd_from_arrays
from database import SessionLocal

import csv
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 

from fastapi.responses import Response, StreamingResponse
from typing import Literal

# Import your updated models
from models import (
    ResultsY,
    ResultsAmp,
    ResultsWelch,
    Algorithm,
    Session as SessionModel,
)

# ── Kalman variant imports (unchanged) ────────────────────────────────────
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # <-- your React dev origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map variant→run() as before
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
MAX_FLOAT32 = 3.4e38  # MySQL FLOAT max

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_algorithm(db: Session, variant_name: str) -> Algorithm:
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

def store_y_result(
    db: Session,
    session_id: int,
    algorithm_id: int,
    label: str,
    y_value: float,
    time_val: float,
) -> ResultsY:
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

@app.post("/run-kalman", response_model=RunResponse)
async def run_kalman_endpoint(
    variant: str = Form(...),
    wC: str = Form(...),
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1) Validate variant
    if variant not in kalman_variants:
        raise HTTPException(400, f"Unknown variant '{variant}'")

    # 2) Parse wC as JSON list of 14 ints
    try:
        wC_arr = np.array(json.loads(wC), dtype=int)
        assert wC_arr.size == 14
    except Exception:
        raise HTTPException(400, "wC must be JSON list of 14 ints")

    # 3) Save incoming CSV into a temp file
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "file must be a .csv")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    file.file.close()

    # 4) Verify session exists
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")

    # 5) **Write the algorithm_name into the session row:**
    sess.algorithm_name = variant
    db.commit()
    db.refresh(sess)

    # 6) Find or create an Algorithm row (so we can reference algorithm.id in child tables)
    algorithm = get_or_create_algorithm(db, variant)

    # 7) Run the chosen Kalman variant
    try:
        run_fn = kalman_variants[variant]
        amp_all, amp_orig, amp_wc, amp_nwc, y_all, y_wc, y_nwc = run_fn(
            tmp_path, Fs, wC_arr
        )
    except Exception as e:
        raise HTTPException(500, f"Kalman error: {e}")
    finally:
        os.unlink(tmp_path)

    # 8) Turn them into 1D float64 numpy arrays, replace NaN/Inf with zero
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

    # 9) Compute Welch PSD on those four amplitude arrays
    try:
        freqs, psd = psd_from_arrays(amps_raw, fs=Fs, nperseg=Fs)
    except Exception as e:
        raise HTTPException(500, f"Welch error: {e}")

    freqs_clean = np.nan_to_num(np.array(freqs, dtype=float))
    psd_clean: Dict[str, np.ndarray] = {}
    for label in AMP_LABELS:
        psd_clean[label] = np.nan_to_num(np.array(psd[label], dtype=float))

    # 10) Insert every sample of the three Y‐arrays into results_y
    n_samples = len(ys_raw["All"])
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
                label=label,
                y_value=y_val,
                time_val=float(idx),
            )

    # 11) Insert every sample of the four amplitude arrays into results_amplitude
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
                label=label,
                amplitude=amp_val,
                time_val=float(idx),
            )

    # 12) Insert one row per frequency into results_welch
    n_bins = len(freqs_clean)
    for bin_idx in range(n_bins):
        freq_val = float(freqs_clean[bin_idx])
        p_all   = float(psd_clean["All"][bin_idx])
        p_orig  = float(psd_clean["Original"][bin_idx])
        p_wc    = float(psd_clean["WC"][bin_idx])
        p_nwc   = float(psd_clean["NWC"][bin_idx])

        def clamp(v: float) -> float:
            if not np.isfinite(v):
                v = 0.0
            if abs(v) > MAX_FLOAT32:
                v = float(np.sign(v) * MAX_FLOAT32)
            return v

        store_welch_result(
            db=db,
            session_id=session_id,
            algorithm_id=algorithm.id,
            frequency=freq_val,
            power_all    = clamp(p_all),
            power_original = clamp(p_orig),
            power_wc     = clamp(p_wc),
            power_nwc    = clamp(p_nwc),
        )

    # 13) Return full time‐series arrays as JSON for any client‐side plotting
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


@app.get("/results/{session_id}")
async def get_session_results(
    session_id: int,
    db: Session = Depends(get_db),
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
                # ← You can still pull algorithm’s name from the Algorithm table if needed:
                "algorithm_name": (r.algorithm.name if r.algorithm else None),
            }
            for r in rows
        ],
    }


# … (the other CSV‐download, amplitude‐array, welch‐array, PNG‐plot endpoints remain unchanged) …



# 3) Stream CSV of ResultsY / ResultsAmp / ResultsWelch for a given session
@app.get("/sessions/{session_id}/results/csv")
def download_results_csv(
    session_id: int,
    type: Literal["y", "amp", "welch"],
    db: Session = Depends(get_db),
):
    """
    Stream one of the three result tables as a CSV attachment:
      • type="y"     → results_y
      • type="amp"   → results_amplitude
      • type="welch" → results_welch
    """
    # 3a) Verify session exists
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(404, detail="Session not found")

    # 3b) Build header row + row‐tuples depending on `type`
    if type == "y":
        query = (
            db.query(ResultsY)
            .filter(ResultsY.session_id == session_id)
            .order_by(ResultsY.time.asc())
            .all()
        )
        headers = ["id", "session_id", "algorithm_id", "label", "y_value", "time"]
        rows = [
            (r.id, r.session_id, r.algorithm_id, r.label, r.y_value, r.time)
            for r in query
        ]

    elif type == "amp":
        query = (
            db.query(ResultsAmp)
            .filter(ResultsAmp.session_id == session_id)
            .order_by(ResultsAmp.time.asc())
            .all()
        )
        headers = ["id", "session_id", "algorithm_id", "label", "amplitude", "time"]
        rows = [
            (r.id, r.session_id, r.algorithm_id, r.label, r.amplitude, r.time)
            for r in query
        ]

    else:  # type == "welch"
        query = (
            db.query(ResultsWelch)
            .filter(ResultsWelch.session_id == session_id)
            .order_by(ResultsWelch.frequency.asc())
            .all()
        )
        headers = [
            "id",
            "session_id",
            "algorithm_id",
            "frequency",
            "power_all",
            "power_original",
            "power_wc",
            "power_nwc",
        ]
        rows = [
            (
                r.id,
                r.session_id,
                r.algorithm_id,
                r.frequency,
                r.power_all,
                r.power_original,
                r.power_wc,
                r.power_nwc,
            )
            for r in query
        ]

    # 3c) Stream back as CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    csv_data = buffer.getvalue()
    buffer.close()

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="session_{session_id}_{type}.csv"'
        },
    )


# ────────────────────────────────────────────────────────────────────────────
# 4) Return raw amplitude arrays (All, Original, WC, NWC) for plotting
@app.get("/sessions/{session_id}/results/amplitude")
def get_amplitude_arrays(session_id: int, db: Session = Depends(get_db)):
    """
    Return a JSON object with four amplitude arrays (length = Nsamples):
      {
        "All": [ … ],
        "Original": [ … ],
        "WC": [ … ],
        "NWC": [ … ]
      }
    """
    # 4a) Verify session exists
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(404, detail="Session not found")

    # 4b) Fetch all rows from results_amplitude in ascending time
    rows = (
        db.query(ResultsAmp)
        .filter(ResultsAmp.session_id == session_id)
        .order_by(ResultsAmp.time.asc())
        .all()
    )

    # 4c) Bucket them by label
    amp_dict = {"All": [], "Original": [], "WC": [], "NWC": []}
    for r in rows:
        amp_dict[r.label].append(r.amplitude)

    return amp_dict


# ────────────────────────────────────────────────────────────────────────────
# 5) Return raw Welch‐PSD arrays (frequencies + 4 power columns)
@app.get("/sessions/{session_id}/results/welch")
def get_welch_arrays(session_id: int, db: Session = Depends(get_db)):
    """
    Return JSON of the Welch PSD arrays:
      {
        "frequencies": [ … ],
        "power": {
          "All": [ … ],
          "Original": [ … ],
          "WC": [ … ],
          "NWC": [ … ]
        }
      }
    """
    # 5a) Verify session exists
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(404, detail="Session not found")

    # 5b) Fetch all rows from results_welch in ascending frequency
    rows = (
        db.query(ResultsWelch)
        .filter(ResultsWelch.session_id == session_id)
        .order_by(ResultsWelch.frequency.asc())
        .all()
    )

    freqs         = [r.frequency for r in rows]
    power_all     = [r.power_all for r in rows]
    power_original= [r.power_original for r in rows]
    power_wc      = [r.power_wc for r in rows]
    power_nwc     = [r.power_nwc for r in rows]

    return {
        "frequencies": freqs,
        "power": {
            "All":      power_all,
            "Original": power_original,
            "WC":       power_wc,
            "NWC":      power_nwc,
        },
    }


# ────────────────────────────────────────────────────────────────────────────
# 6) Render “Amplitude vs Time” as PNG
@app.get("/sessions/{session_id}/plot/amplitude.png")
def plot_amplitude_png(session_id: int, db: Session = Depends(get_db)):
    """
    Fetch the four amplitude arrays from the database,
    plot them on a Matplotlib figure, and stream as PNG.
    """
    # 6a) Re‐use get_amplitude_arrays() to retrieve the arrays
    amp_dict = get_amplitude_arrays(session_id, db)
    arr_all      = np.array(amp_dict["All"])
    arr_orig     = np.array(amp_dict["Original"])
    arr_wc       = np.array(amp_dict["WC"])
    arr_nwc      = np.array(amp_dict["NWC"])

    n_samples = arr_orig.shape[0]
    times = np.arange(n_samples)

    # 6b) Create figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(times, arr_orig, label="Original", color="black", linewidth=1)
    ax.plot(times, arr_all,  label="All",      color="magenta", alpha=0.7, linewidth=1)
    ax.plot(times, arr_wc,   label="WC",       color="green",   alpha=0.7, linewidth=1)
    ax.plot(times, arr_nwc,  label="NWC",      color="blue",    alpha=0.7, linewidth=1)
    ax.set_title(f"Session {session_id} – Amplitude vs Time")
    ax.set_xlabel("Time (sample index)")
    ax.set_ylabel("Amplitude")
    ax.legend(loc="upper right")
    ax.grid(True)

    # 6c) Write figure to in-memory buffer
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


# ────────────────────────────────────────────────────────────────────────────
# 7) Render “Welch PSD” as PNG
@app.get("/sessions/{session_id}/plot/welch.png")
def plot_welch_png(session_id: int, db: Session = Depends(get_db)):
    """
    Fetch Welch‐PSD arrays from the database,
    plot power vs frequency for all four labels, and stream as PNG.
    """
    # 7a) Re‐use get_welch_arrays() to retrieve the arrays
    welch_resp = get_welch_arrays(session_id, db)
    freqs       = np.array(welch_resp["frequencies"])
    p_all       = np.array(welch_resp["power"]["All"])
    p_orig      = np.array(welch_resp["power"]["Original"])
    p_wc        = np.array(welch_resp["power"]["WC"])
    p_nwc       = np.array(welch_resp["power"]["NWC"])

    # 7b) Create figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(freqs, p_orig,  label="Original", color="black", linewidth=1)
    ax.plot(freqs, p_all,   label="All",      color="red",    alpha=0.7, linewidth=1)
    ax.plot(freqs, p_wc,    label="WC",       color="green",  alpha=0.7, linewidth=1)
    ax.plot(freqs, p_nwc,   label="NWC",      color="blue",   alpha=0.7, linewidth=1)
    ax.set_title(f"Session {session_id} – Welch Power Spectral Density")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power")
    ax.legend(loc="upper right")
    ax.grid(True)

    # 7c) Write figure to buffer
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")