import os
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def Wilcoxon(data1, data2):
    statistic, p = wilcoxon(data1, data2)
    return statistic, p

# Input and output folders
input_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WELCH'
output_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WILCOXON'

os.makedirs(output_folder, exist_ok=True)

# List all session files
session_files = sorted(
    [f for f in os.listdir(input_folder) if f.endswith('_welch.csv') and f.startswith('S')],
    key=lambda x: int(x.split('_')[0][1:])  # Sort numerically by session number (e.g., S1, S2, ...)
)

results = []

# Perform Wilcoxon signed-rank test for each pair of sessions
for i in range(len(session_files) - 1):
    session_from = session_files[i].split('_')[0]
    session_to = session_files[i + 1].split('_')[0]
    
    file_from = os.path.join(input_folder, session_files[i])
    file_to = os.path.join(input_folder, session_files[i + 1])
    
    # Read the data
    data_from = pd.read_csv(file_from)
    data_to = pd.read_csv(file_to)
    
    # Extract the entire `Power_WC` column
    power_from = data_from['Power_WC'].values
    power_to = data_to['Power_WC'].values
    
    # Perform Wilcoxon test
    statistic, p_value = Wilcoxon(power_from, power_to)
    results.append([session_from, session_to, statistic, p_value])

# Add the last session to the first session (S19 -> S1)
session_from = session_files[-1].split('_')[0]
session_to = session_files[0].split('_')[0]

file_from = os.path.join(input_folder, session_files[-1])  
file_to = os.path.join(input_folder, session_files[0])  

data_from = pd.read_csv(file_from)
data_to = pd.read_csv(file_to)

power_from = data_from['Power_WC'].values
power_to = data_to['Power_WC'].values

statistic, p_value = Wilcoxon(power_from, power_to)
results.append([session_from, session_to, statistic, p_value])

# Save the results to a CSV file
output_file = os.path.join(output_folder, 'wilcoxon_wc_results.csv')
results_df = pd.DataFrame(results, columns=['From_Session', 'To_Session', 'Statistic', 'P_Value'])
results_df.to_csv(output_file, index=False)

print(f"Wilcoxon test results saved to {output_file}")
