import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Define Welch function
def Welch(signal, fs=128, nperseg=128):
    f, Pxx = welch(signal, fs=fs, nperseg=nperseg)
    return f, Pxx

# Input folder
input_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN'

# Initialize storage for Welch results
amplitude_types = ["All", "Original", "WC", "NWC"]
results = {}

# Process files for session S1
for file_name in os.listdir(input_folder):
    if file_name.startswith('S1') and file_name.endswith('.csv') and "amplitude" in file_name:
        file_path = os.path.join(input_folder, file_name)
        amp_type = file_name.split("_")[-1].replace(".csv", "")  
        
        print(f"Processing {file_name}...")

        amplitude_data = np.loadtxt(file_path, delimiter=',')
        f, Pxx = Welch(amplitude_data)
        results[amp_type] = (f, Pxx)

# Plot the Welch PSD for session S1
plt.figure(figsize=(10, 6))
colors = {"All": "red", "Original": "blue", "WC": "green", "NWC": "black"}
markers = {"All": "o", "Original": "s", "WC": "^", "NWC": "x"}

for amp_type, (f, Pxx) in results.items():
    plt.plot(f, 10 * np.log10(Pxx), label=amp_type, color=colors[amp_type], marker=markers[amp_type], markersize=5)

plt.title("Welch PSD for S1")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power Spectral Density (dB)")
plt.legend(title="Amplitude Types")
plt.grid()
plt.show()
