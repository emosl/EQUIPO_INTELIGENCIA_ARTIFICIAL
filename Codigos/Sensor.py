import os
import pandas as pd
import matplotlib.pyplot as plt

current_path = os.path.dirname(__file__) # Get the directory of the current script
file_path = '../Procesado/S1_procesado.csv' # Replace with the path to your CSV file
rel_path = os.path.join(current_path, file_path) # The relative path to the CSV file to plot

data = pd.read_csv(rel_path) # Read the CSV file

def plot(data):
    """
    This function plots the sensor data from a given dataset or session, 
    displaying the comparison between the original and the filtered signals.

    Parameters:
        - data (pandas.DataFrame): The dataset or session to be plotted.

    It does so by:  
        1. Defining a list of sensor labels (choosing the sensors you want to plot).
        2. Extracting the sensor data from the dataset.
        3. Creating a time axis.
        4. Creating subplots for each sensor.
        5. Plotting the original and filtered signals for each sensor.
        6. Setting the plot title, labels, and colors.
        7. Adjusting the layout and showing the plot.
    """ 
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

plot(data)