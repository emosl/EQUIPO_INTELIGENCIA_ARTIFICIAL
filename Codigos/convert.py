import os
import mne
import pandas as pd

# adjust these two paths to match yours
ica_dir    = "/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/ICA_4/ICA_Omar"
output_dir = "/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN/KALMAN_Omar"

os.makedirs(output_dir, exist_ok=True)

for i in range(2, 21):
    set_fname  = f"S{i}_ICA.set"
    in_path    = os.path.join(ica_dir, set_fname)
    out_fname  = f"S{i}.csv"
    out_path   = os.path.join(output_dir, out_fname)

    # load the EEGLAB dataset (automatically reads the .fdt)
    raw = mne.io.read_raw_eeglab(in_path, preload=True)

    # get data (n_channels × n_samples) and time vector (in seconds)
    data = raw.get_data()
    times_s = raw.times

    # build a DataFrame: first column = Time (ms), then one column per channel
    df = pd.DataFrame(data.T, columns=raw.ch_names)
    df.insert(0, "Time", times_s * 1000)  # convert to milliseconds

    # write CSV with four decimal places
    df.to_csv(out_path, index=False, float_format="%.4f")
    print(f"Wrote {out_path}")
