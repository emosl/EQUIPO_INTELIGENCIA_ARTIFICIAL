import numpy as np
input_path_amplitude_all = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN/S1_amplitude_All.csv'
input_path_amplitude_WC = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN/S1_amplitude_WC.csv'
input_path_amplitude_NWC = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN/S1_amplitude_NWC.csv'
output_file = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/GRAFICAS/histogram.png'
amplitude_all = np.loadtxt(input_path_amplitude_all, delimiter=',')
amplitude_WC = np.loadtxt(input_path_amplitude_WC, delimiter=',')
amplitude_NWC = np.loadtxt(input_path_amplitude_NWC, delimiter=',')

#noramilze amplitude 
amplitude_all = amplitude_all / np.max(amplitude_all)
amplitude_WC = amplitude_WC / np.max(amplitude_WC)
amplitude_NWC = amplitude_NWC / np.max(amplitude_NWC)

#histogram of normalized amplitude
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.hist(amplitude_WC, bins=22, alpha=0.7, label='WC Sensors', color='purple')
plt.hist(amplitude_all, bins=22, alpha=0.9, label='All Sensors', color='pink')
plt.hist(amplitude_NWC, bins=22, alpha=0.7, label='NWC Sensors', color='green')
plt.title('Histogram of Normalized Amplitude')
plt.xlabel('Amplitude')
plt.ylabel('Frequency')
plt.legend()
plt.grid()

plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.close()

print(f"Log-scaled plot saved to {output_file}")