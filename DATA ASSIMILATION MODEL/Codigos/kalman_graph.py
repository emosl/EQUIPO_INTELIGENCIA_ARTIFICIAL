import numpy as np 
input_original_amplitude = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos/S1_amplitude_Original.csv'
input_all_amplitude = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos/S1_amplitude_All.csv'
input_WC_amplitude = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos/S1_amplitude_WC.csv'
input_NWC_amplitude = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos/S1_amplitude_NWC.csv'
output_file = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/Codigos'       

amplitude_original = np.loadtxt(input_original_amplitude, delimiter=',')
amplitude_all = np.loadtxt(input_all_amplitude, delimiter=',')
amplitude_WC = np.loadtxt(input_WC_amplitude, delimiter=',')
amplitude_NWC = np.loadtxt(input_NWC_amplitude, delimiter=',')

time = np.arange(len(amplitude_original))
# Plot the original and predicted signals for session S10
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(time, amplitude_original, label='Original Signal', color='black')
plt.plot(time, amplitude_all, label='Predicted Signal (All Sensors)', color='magenta', alpha=0.6)
plt.title('Original vs Predicted Signal (All Sensors)')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.grid()
plt.show()

