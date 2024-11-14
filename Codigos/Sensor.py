import pandas as pd
import matplotlib.pyplot as plt

file_path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/INTELIGENCIA_ARTIFICIAL/SEGUNDO_BLOQUE/LIZ/FILTRADO1/Cognitiv Anakaren Session 12.csv'

data = pd.read_csv(file_path)
data.columns = data.columns.str.strip()  

#sensor_labels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
sensor_labels = ['AF3', 'F7']
filtered_data = data[sensor_labels]

time = range(len(filtered_data))

fig, axs = plt.subplots(len(sensor_labels), 1, figsize=(10, 30))

for i, label in enumerate(sensor_labels):
    sensor_data = filtered_data[label]
    axs[i].plot(time, sensor_data, color='lightsteelblue') 
    axs[i].set_title(f'Sensor {label}: Comparacion de Señal Original y Filtrada')
    axs[i].set_xlabel('Sample Number')
    axs[i].set_ylabel('Sensor Reading')
    axs[i].set_facecolor('slategray')
    axs[i].grid(True, color='darkslategray')

plt.tight_layout()
plt.show()
