#!/usr/bin/env python3
import os
import numpy as np
from Kalman_Givens_Bierman import run

def main():
    input_csv = "/Users/emiliasalazar/Downloads/Results/EXCECUTION_TIMES/Kalman Filter Ensemble Pre2 (2).csv"
    output_dir = "/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos"
    Fs = 128
    wC = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1], dtype=int)

    os.makedirs(output_dir, exist_ok=True)

    print("🔍 Running Householder‐Potter Kalman on:", input_csv)
    resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC = run(input_csv, Fs, wC)
    print("✅ Kalman run complete.")

    amplitudeAll      = resultAll.flatten()
    amplitudeOriginal = resultOriginal.flatten()
    amplitudeWC       = resultWC.flatten()
    amplitudeNWC      = resultNWC.flatten()
    amplitudeYAll  = np.array(yAll)
    amplitudeYWC   = np.array(yWC)
    amplitudeYNWC  = np.array(yNWC)

    prefix = "S1"  # change if needed
    fn_orig  = os.path.join(output_dir, f"{prefix}_amplitude_Original.csv")
    fn_all   = os.path.join(output_dir, f"{prefix}_amplitude_All.csv")
    fn_wc    = os.path.join(output_dir, f"{prefix}_amplitude_WC.csv")
    fn_nwc   = os.path.join(output_dir, f"{prefix}_amplitude_NWC.csv")
    fn_y_all = os.path.join(output_dir, f"{prefix}_y_All.csv")
    fn_y_wc  = os.path.join(output_dir, f"{prefix}_y_WC.csv")
    fn_y_nwc = os.path.join(output_dir, f"{prefix}_y_NWC.csv")

    np.savetxt(fn_orig,  amplitudeOriginal, fmt="%.6f", delimiter="\n")
    np.savetxt(fn_all,   amplitudeAll,      fmt="%.6f", delimiter="\n")
    np.savetxt(fn_wc,    amplitudeWC,       fmt="%.6f", delimiter="\n")
    np.savetxt(fn_nwc,   amplitudeNWC,      fmt="%.6f", delimiter="\n")
    np.savetxt(fn_y_all, amplitudeYAll,     fmt="%.6f", delimiter="\n")
    np.savetxt(fn_y_wc,  amplitudeYWC,      fmt="%.6f", delimiter="\n")
    np.savetxt(fn_y_nwc, amplitudeYNWC,     fmt="%.6f", delimiter="\n")

    print("🏁 All CSVs saved.")

if __name__ == "__main__":
    main()
