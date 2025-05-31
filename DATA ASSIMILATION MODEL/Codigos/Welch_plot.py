
import os
import numpy as np
import matplotlib.pyplot as plt

input_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WELCH'
output_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WELCH_PLOTS'

os.makedirs(output_folder, exist_ok=True)

colors = {"Power_All": "red", "Power_Original": "blue", "Power_WC": "green", "Power_NWC": "black"}
markers = {"Power_All": "o", "Power_Original": "s", "Power_WC": "^", "Power_NWC": "x"}


for file_name in os.listdir(input_folder):
    if file_name.endswith('_welch.csv') and file_name.startswith('S'): 
        file_path = os.path.join(input_folder, file_name)
        session = os.path.splitext(file_name)[0] 
        print(f"Processing {session}...")


        data = np.loadtxt(file_path, delimiter=',', skiprows=1)  
        frequencies = data[:, 0]  
        plt.figure(figsize=(10, 6))
        plt.title(f"Welch PSD for {session}", fontsize=16)
        plt.xlabel("Frequency (Hz)", fontsize=14)
        plt.ylabel("Power Spectral Density (dB)", fontsize=14)
        plt.grid(True)


        headers = ["Power_All", "Power_NWC", "Power_Original", "Power_WC"]
        for i, header in enumerate(headers, start=1): 
            plt.plot(
                frequencies,
                data[:, i], 
                label=header.replace("Power_", ""), 
                color=colors.get(header, "gray"),
                marker=markers.get(header, "o"),
                markersize=5,
                linewidth=1.5
            )

        plt.legend(title="Amplitude Types", fontsize=12)
        plt.tight_layout()

        plot_path = os.path.join(output_folder, f"{session}_plot.png")
        plt.savefig(plot_path, dpi=300)
        plt.close()

        print(f"Saved plot for {session} to {plot_path}")

print("All plots created and saved.")
