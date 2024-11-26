import matplotlib.pyplot as plt
import numpy as np

# File paths
amplitudeOriginal_path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN/S7_amplitude_Original.csv'
amplitudeAll_path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN/S7_amplitude_All.csv'


amplitudeOriginal = np.loadtxt(amplitudeOriginal_path, delimiter=',')
amplitudeAll = np.loadtxt(amplitudeAll_path, delimiter=',')

time = np.arange(len(amplitudeOriginal))

plt.figure(figsize=(12, 6))
plt.plot(time, amplitudeOriginal, label='Original Signal', color='blue')
plt.plot(time, amplitudeAll, label='Predicted Signal (All Sensors)', color='red', alpha=0.7)
plt.title('Original vs Predicted Signal (All Sensors)')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.grid()
plt.show()
