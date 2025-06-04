# welch.py  ──────────────────────────────────────────────────────────────────
import os
from typing import Dict, Tuple

import numpy as np
from scipy.signal import welch

# ── helper ────────────────────────────────────────────────────────────────
def _welch(signal: np.ndarray, fs: int = 128, nperseg: int = 128):
    f, Pxx = welch(signal, fs=fs, nperseg=nperseg)
    return f, 10.0 * np.log10(Pxx)

def psd_from_arrays(
    amps: Dict[str, np.ndarray], *,
    fs: int = 128, nperseg: int = 128
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Compute with *all* amplitude vectors in memory."""
    freqs, psd = None, {}
    for lab, sig in amps.items():
        if sig.size == 0:
            raise ValueError(f"No samples for label '{lab}'")
        f, P = _welch(sig, fs=fs, nperseg=nperseg)
        if freqs is None:
            freqs = f
        psd[lab] = P
    return freqs, psd

# ── disk writer (optional) ────────────────────────────────────────────────
def run(
    session: str,
    input_folder: str,
    output_folder: str,
    *,
    fs: int = 128,
    nperseg: int = 128,
    labels=None,
    verbose: bool = True,
):
    """Write one CSV per session with four Power_* columns."""
    if labels is None:
        labels = ["All", "NWC", "Original", "WC"]

    os.makedirs(output_folder, exist_ok=True)
    if verbose:
        print(f"Processing session {session} …")

    amps: Dict[str, np.ndarray] = {}
    for lab in labels:
        path = os.path.join(input_folder, f"{session}_amplitude_{lab}.csv")
        if os.path.exists(path):
            amps[lab] = np.loadtxt(path, delimiter=",")
        elif verbose:
            print(f"  · missing {path}")

    if not amps:
        if verbose:
            print("  · no valid data; nothing written")
        return None

    freqs, psd = psd_from_arrays(amps, fs=fs, nperseg=nperseg)

    # fill missing labels with zeros
    for lab in labels:
        if lab not in psd:
            psd[lab] = np.zeros_like(freqs)

    out_csv = os.path.join(output_folder, f"{session}_welch.csv")
    with open(out_csv, "w") as fh:
        fh.write("Frequency," + ",".join(f"Power_{lab}" for lab in labels) + "\n")
        for i, fval in enumerate(freqs):
            row = [fval] + [psd[lab][i] for lab in labels]
            fh.write(",".join(map(str, row)) + "\n")

    if verbose:
        print(f"  · saved {out_csv}")
    return out_csv
