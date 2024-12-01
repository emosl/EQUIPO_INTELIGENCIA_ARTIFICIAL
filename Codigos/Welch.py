import os
import numpy as np
from scipy.signal import welch


def Welch(signal, fs=128, nperseg=128):
    #returns frequency and power spectral density, bultiplying by 10 logarithmically to get dB
    f, Pxx = welch(signal, fs=fs, nperseg=nperseg)
    return f, 10 * np.log10(Pxx)  


# Input and output folders
input_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN'
output_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WELCH'

os.makedirs(output_folder, exist_ok=True)

# Define sessions and labels
sessions = [f"S{i}" for i in range(1, 20)]  # Generate session names S1 to S19
labels = ["All", "NWC", "Original", "WC"]  # Amplitude types

for session in sessions:
    print(f"Processing session {session}...")

    session_data = {}
    frequencies = None

    for label in labels:
        # Construct the file path
        file_name = f"{session}_amplitude_{label}.csv"
        file_path = os.path.join(input_folder, file_name)

        if os.path.exists(file_path):
            # Load amplitude data and calculate Welch PSD
            amplitude_data = np.loadtxt(file_path, delimiter=',')
            f, Pxx = Welch(amplitude_data)

            if frequencies is None:
                frequencies = f  # Save frequencies from the first valid file

            session_data[label] = Pxx
        else:
            print(f"Missing file for {session} - {label}. Filling with zeros.")
            session_data[label] = np.zeros_like(frequencies) if frequencies is not None else None

    # Skip session if no data found
    if frequencies is None:
        print(f"No valid data found for session {session}. Skipping.")
        continue

    # Save results for the session in a single CSV
    output_path = os.path.join(output_folder, f"{session}_welch.csv")
    with open(output_path, 'w') as file:
        # Write the header
        header = "Frequency," + ",".join([f"Power_{label}" for label in labels])
        file.write(header + "\n")

        # Write rows
        for i in range(len(frequencies)):
            row = [frequencies[i]] + [session_data[label][i] if session_data[label] is not None else 0 for label in labels]
            file.write(",".join(map(str, row)) + "\n")

    print(f"Saved Welch results for session {session} to {output_path}")

print("All sessions processed.")
