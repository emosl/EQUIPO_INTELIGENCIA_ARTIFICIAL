import os
import math
import numpy as np
import pandas as pd

from scipy import signal

order = 4 # Order of the filter
file_count = 19 # Number of files
chunk_size = 128 # Samples in each second
low_cutoff = 8/64 # Nyquist frequency for low cutoff
high_cutoff = 16/64 # Nyquist frequency for high cutoff
sampling_rate = 128 # Sampling rate

counter_cols = [0] # Counter column of the dataset
columns_to_use = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] # The columns that contain sensor information
column_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'] # The names of the sensors

file_prefix  = 'S'
start_sess   = 2       # first session to process
end_sess     = 20      # last session to process
input_dir    = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Grabaciones/Grabaciones_Rafael'
output_dir   = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Procesado_1/Procesado_Rafael'



def cropData(data):
    """
    This function traverses a given dataset and searches for repeated values in 
    the counter column and then drops the corresponding rows in the dataset.

    Parameters:
        - data (pandas.DataFrame): The dataset to be processed.

    It does so by:
        1. Resetting the index of the dataset.
        2. Reading the counter column from the dataset.
        3. Creating a list of indices to drop based on the counter column.
        4. Dropping the indices from the dataset.

    Returns:
        - filtered_data (pandas.DataFrame): The dataset with repeated values removed.
    """
    data.reset_index(drop=True, inplace=True)
    counter = pd.read_csv(input_path, usecols=counter_cols)
    trueCounter = np.array(counter.index[:])
    indicesToDrop = []
    checkpoint = 1

    for i in range(len(trueCounter)):
        if trueCounter[checkpoint] == trueCounter[i]:
            indicesToDrop.append(i)
        checkpoint = i

    return data.drop(indicesToDrop), indicesToDrop

def detect_repeated_values(data, threshold=38400):
    """
    This function traverses a given dataset and searches for repeated values in 
    each column. If repeated values are found, it prints a warning message and 
    returns a list of error messages.

    Parameters:
        - data (pandas.DataFrame): The dataset to be processed.
        - threshold (int, optional): The threshold for repeated values in number of samples. Defaults to 38400 or 300 seconds.

    It does so by:
        1. Iterating over each column in the dataset.
        2. Counting the repeated values in each column.
        3. Checking if any value count exceeds the threshold.
        4. If a repeated value is found, it prints a warning message and returns a list of error messages.

    Returns:  
        - tensor (numpy.ndarray): A 3D tensor containing the processed data.  
        - error_messages (list): A list of error messages.
    """
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

def removeDCPassFilter(array, order, low, high, Fs):
    """
    This function applies a Butterworth bandpass filter to a given array. And
    returns a new array with the filtered data.

    Parameters:
        - array (numpy.ndarray): A 2D input array to be filtered.
        - order (int): The order of the filter.
        - low (float): The lower cutoff frequency of the filter.
        - high (float): The higher cutoff frequency of the filter.
        - Fs (float): The sampling rate of the data.
    
    It does so by: 
        1.- Applying the scipy implementation of the butterworth filter 
        `butter`.
        2.- It then creates a new array of the same shape as the input array 
        filled with zeros.
        3.- Next, it applies the `filtfilt` function to each element of the 
        input array to remove phase distortion.
        4.- Finally, it deletes the rows of the new array that have all zeros in 
        them.

    Returns:
        - newArray (numpy.ndarray): A 2D array with the filtered data.
    """
    b, a = signal.butter(order, [low, high], 'band')
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

def process_file(input_path, output_path):
    data = pd.read_csv(input_path, usecols=columns_to_use, names=column_names, header=0, skipinitialspace=True)
    filtered_data = data.iloc[:, :]

    filtered_data, dropped_indices = cropData(filtered_data)
    
    print(f"Reading file: {input_path}")
    print("Data head:\n", data.head())  
    

    tensor, error_messages = detect_repeated_values(filtered_data, threshold=23040)  
    if tensor is None:
        print(f"Skipping processing for {input_path} due to repeated values exceeding threshold.")
        for message in error_messages:
            print(message)
        return 
    final_tensor = removeDCPassFilter(tensor, order=4, low=low_cutoff, high=high_cutoff, Fs=sampling_rate)
    

    flat_data = final_tensor.reshape(-1, final_tensor.shape[1])

    processed_df = pd.DataFrame(flat_data, columns=column_names)
    
    processed_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

for i in range(start_sess, end_sess + 1):
    input_path  = os.path.join(input_dir,  f"{file_prefix}{i}.csv")
    output_path = os.path.join(output_dir, f"{file_prefix}{i}_procesado.csv")
    print(f"Processing file: {input_path}")
    print(f" → Writing to : {output_path}")
    process_file(input_path, output_path)