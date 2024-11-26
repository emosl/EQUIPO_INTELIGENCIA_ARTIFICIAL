import pandas as pd
import numpy as np
import os

def count_seconds_and_difference(file1, file2, chunk_size=128):
    """
    This function computes the number of seconds (128-row matrices) for each file
    and calculates the difference in the number of seconds between the two files.

    Parameters:
        - file1 (str): Path to the first file (e.g., 'Procesado_1/S1_procesado.csv').
        - file2 (str): Path to the second file (e.g., 'KALMAN/S1.csv').
        - chunk_size (int, optional): Number of rows per second. Defaults to 128.

    Returns:
        - seconds_file1 (int): Number of seconds (128-row matrices) in the first file.
        - seconds_file2 (int): Number of seconds (128-row matrices) in the second file.
        - difference (int): Difference in the number of seconds between the two files.
    """
    data1 = pd.read_csv(file1, header=None)
    data2 = pd.read_csv(file2, header=None)

    seconds_file1 = data1.shape[0] // chunk_size
    seconds_file2 = data2.shape[0] // chunk_size

    difference = abs(seconds_file1 - seconds_file2)

    return seconds_file1, seconds_file2, difference

def process_files(base_dir1, base_dir2, chunk_size=128):
    """
    Processes multiple files from two directories and computes the seconds and differences.

    Parameters:
        - base_dir1 (str): Base directory for the first set of files (e.g., 'Procesado_1').
        - base_dir2 (str): Base directory for the second set of files (e.g., 'KALMAN').
        - chunk_size (int, optional): Number of rows per second. Defaults to 128.

    Returns:
        - results (list): List of tuples with (file_name, seconds_file1, seconds_file2, difference).
    """
    results = []
    for i in range(1, 20):  
        file1 = os.path.join(base_dir1, f"S{i}_procesado.csv")
        file2 = os.path.join(base_dir2, f"S{i}.csv")

        if os.path.exists(file1) and os.path.exists(file2):
            seconds_file1, seconds_file2, difference = count_seconds_and_difference(file1, file2, chunk_size)
            results.append((f"S{i}", seconds_file1, seconds_file2, difference))
        else:
            print(f"Skipping files: {file1} or {file2} not found")

    return results

base_dir1 = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Procesado_1'
base_dir2 = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN'

results = process_files(base_dir1, base_dir2)

for file_name, sec1, sec2, diff in results:
    print(f"{file_name}: File1 seconds={sec1}, File2 seconds={sec2}, Difference={diff}")
