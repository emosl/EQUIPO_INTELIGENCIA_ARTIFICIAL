import pandas as pd
import numpy as np
from scipy import signal
import os
import math


columns_to_use = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
column_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
chunk_size = 128

def detect_repeated_values(data, threshold=38400):
    error_messages = []
    sessionMatrix = []
    
    for column in data.columns:
        repetitions = data[column].value_counts()
        exceeding_values = repetitions[repetitions > threshold]
        
        if not exceeding_values.empty:
            print(f"Repeated values found in column {column} across the entire dataset:")
            print(exceeding_values)
            error_messages.append(
                f"Warning: Repeated values in column {column} exceed threshold in the entire dataset"
            )
    
    for i in range(0, data.shape[0], chunk_size):
        chunk = data.iloc[i:i + chunk_size]
        
        if len(chunk) < chunk_size:
            print(f"Skipping incomplete chunk at rows {i} to {i + len(chunk)} (size {len(chunk)})")
            continue
        
        has_error = False
        for column in chunk.columns:
            chunk_repetitions = chunk[column].value_counts()
            if any(chunk_repetitions > threshold):
                print(f"Warning: Repeated values found in column {column} for rows {i} to {i + chunk_size}")
                has_error = True
                error_messages.append(
                    f"Warning: Repeated values in column {column} exceed threshold in rows {i} to {i + chunk_size}"
                )
                break

       
        if not has_error:
            #print(f"Adding chunk rows {i} to {i + chunk_size}")
            sessionMatrix.append(chunk.values)
    
    tensor = np.array(sessionMatrix)
    tensor = np.transpose(tensor, (0, 2, 1)) 
    print(f"sessionMatrix shape after processing and transposing: {tensor.shape}")

    return tensor, error_messages



def getFilter(order, low, high):
    return signal.butter(order, [low, high], 'band')


def removeDC(array):
    newArray = np.full_like(array, 0)
    second = 0

    for i in range(len(array)):
        for j in range(array.shape[1]):
            meanA = np.mean(array[i][j])
            newArray[i][j] = array[i][j] - meanA     
    
    for k in range(len(newArray)):
        x = np.where(~newArray[second].any(axis=1))[0]
        if x.size == 0:
            second += 1
        else:
            newArray = np.delete(newArray, second, 0)
                
    return newArray


def removeDCPassFilter(array, threshold, Fs):
    b, a = signal.butter(1, threshold, 'high')
    newArray = np.full_like(array, 0)
    second = 0
    
    for i in range(len(array)):
        for j in range(len(array[i])):
            newArray[i][j] = signal.filtfilt(b, a, array[i][j])
    
    for k in range(len(newArray)):
        tempA = (newArray[second] == 0).sum(axis=1)
        x = np.argwhere(tempA > math.ceil(Fs / 10))
        if x.size == 0:
            second += 1
        else:
            newArray = np.delete(newArray, second, 0)
        
    return newArray


def apply_bandpass_filter(tensor, b, a):
    filtered_tensor = np.zeros_like(tensor)
    for i in range(len(tensor)):
        for j in range(tensor.shape[1]):
            filtered_tensor[i, j, :] = signal.filtfilt(b, a, tensor[i, j, :])
    return filtered_tensor


input_dir = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Grabaciones/'
output_dir = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Procesado/'
file_prefix = 'S'
file_count = 19
order = 4
low_cutoff = 8
high_cutoff = 32
sampling_rate = 128
b, a = getFilter(order, low_cutoff / (0.5 * sampling_rate), high_cutoff / (0.5 * sampling_rate))


def process_file(input_path, output_path):
    data = pd.read_csv(input_path, usecols=columns_to_use, names=column_names, header=0, skipinitialspace=True)
    filtered_data = data.iloc[:, :]
    
    print(f"Reading file: {input_path}")
    print("Data head:\n", data.head())  
    

    tensor, error_messages = detect_repeated_values(filtered_data, threshold=23040)  
    if tensor is None:
        print(f"Skipping processing for {input_path} due to repeated values exceeding threshold.")
        for message in error_messages:
            print(message)
        return 

    tensor = removeDC(tensor)
    bandpassed_tensor = apply_bandpass_filter(tensor, b, a)
    final_tensor = removeDCPassFilter(bandpassed_tensor, threshold=0.16, Fs=sampling_rate)

    flat_data = final_tensor.transpose(0, 2, 1).reshape(-1, final_tensor.shape[1])

    processed_df = pd.DataFrame(flat_data, columns=column_names)
    
    processed_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")



for i in range(1, file_count + 1):
    input_path = os.path.join(input_dir, f"{file_prefix}{i}.csv")
    output_path = os.path.join(output_dir, f"{file_prefix}{i}_procesado.csv")
    
    process_file(input_path, output_path)
