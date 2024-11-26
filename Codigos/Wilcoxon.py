# import os
# import numpy as np
# import pandas as pd
# from scipy.stats import wilcoxon


# def Wilcoxon(data1, data2):
#     statistic, p = wilcoxon(data1, data2)
#     return statistic, p


# input_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WELCH'
# output_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WILCOXON'

# os.makedirs(output_folder, exist_ok=True)


# frequencies_of_interest = [8.0, 9.0, 10.0, 11.0, 12.0]

# session_files = sorted(
#     [f for f in os.listdir(input_folder) if f.endswith('_welch.csv') and f.startswith('S')],
#     key=lambda x: int(x.split('_')[0][1:])  
# )

# results = []

# for i in range(len(session_files) - 1):
#     session_from = session_files[i].split('_')[0]
#     session_to = session_files[i + 1].split('_')[0]
    
#     file_from = os.path.join(input_folder, session_files[i])
#     file_to = os.path.join(input_folder, session_files[i + 1])
    
#     data_from = pd.read_csv(file_from)
#     data_to = pd.read_csv(file_to)
    
#     power_from = data_from[data_from['Frequency'].isin(frequencies_of_interest)]['Power_WC'].values
#     power_to = data_to[data_to['Frequency'].isin(frequencies_of_interest)]['Power_WC'].values
#     statistic, p_value = Wilcoxon(power_from, power_to)
#     results.append([session_from, session_to, statistic, p_value])

# session_from = session_files[-1].split('_')[0]
# session_to = session_files[0].split('_')[0]

# file_from = os.path.join(input_folder, session_files[-1])  
# file_to = os.path.join(input_folder, session_files[0])  

# data_from = pd.read_csv(file_from)
# data_to = pd.read_csv(file_to)

# power_from = data_from[data_from['Frequency'].isin(frequencies_of_interest)]['Power_WC'].values
# power_to = data_to[data_to['Frequency'].isin(frequencies_of_interest)]['Power_WC'].values
# statistic, p_value = Wilcoxon(power_from, power_to)

# results.append([session_from, session_to, statistic, p_value])
# output_file = os.path.join(output_folder, 'wilcoxon_results.csv')
# results_df = pd.DataFrame(results, columns=['From_Session', 'To_Session', 'Statistic', 'P_Value'])
# results_df.to_csv(output_file, index=False)

# print(f"Wilcoxon test results saved to {output_file}")

# Data dictionary for all sessions
# sessions = {
#     "S1": [
#         -0.6206740775909075, -1.3935964701696069, -1.2496445371196279, -1.0130008207823487, -0.9949595128592665
#     ],
#     "S2": [
#         1.3942745941799224, 1.0958941715409427, 0.7975057180013084, 1.0294379319675437, 1.421347275436898
#     ],
#     "S3": [
#         2.6421932831373596, 4.266320499870442, 5.005059232328471, 5.547600723069736, 6.16035724980455
#     ],
#     "S4": [
#         1.140735105499343, 0.6372193966521182, -0.12554170663373876, -0.5380584024981009, -0.6242319385343335
#     ],
#     "S5": [
#         2.9731413063861845, 3.8090895735883743, 4.023827120373893, 4.441775312132275, 5.62425501755494
#     ],
#     "S6": [
#         2.9639417274722617, 3.4649311077130216, 5.04928428814746, 5.061537310707043, 6.014734790503486
#     ],
#     "S7": [
#         -2.697521353424586, -3.856516925706272, -3.239038331138147, -1.7172340947707858, -1.0303004891648628
#     ],
#     "S8": [
#         -2.402183184109365, -1.5291235662953595, -0.7468372386407223, -0.9918715643393422, -0.03651634051951139
#     ],
#     "S9": [
#         0.3786275311097561, 0.23997516985972767, -0.6723624422575574, -0.12423513035322131, 0.013614014098118965
#     ],
#     "S10": [
#         -4.504734181943034, -4.989381051899693, -4.95308394423973, -4.118296746406541, -2.83648110069634
#     ],
#     "S11": [
#         5.436261953275407, 4.359181183263969, 3.280654654759299, 2.3628813865606153, 1.7474846221667537
#     ],
#     "S12": [
#         6.122746744213806, 7.181658139709256, 7.4742998098692635, 7.049130418326395, 6.497501491606503
#     ],
#     "S13": [
#         -3.0181073173982726, -3.4875216318205644, -3.098609216109884, -2.010330868048742, -0.8943278356742386
#     ],
#     "S14": [
#         -1.1221042473912992, -1.17745840215973, -1.3800911543761356, -0.4953573405579621, 0.40646502148410674
#     ],
#     "S15": [
#         1.285249954029291, 0.7640087550562923, 0.21623653489136976, 1.0262258447382202, 2.2509400354760754
#     ],
#     "S16": [
#         0.835061198224155, 0.5655882436222638, 2.010568254960809, 3.6292140750778277, 4.001125089337447
#     ],
#     "S17": [
#         3.045587508823458, 3.1023578990232443, 3.275721679916132, 3.2618006837543865, 3.6163865150464476
#     ],
#     "S18": [
#         4.09260569482315, 4.196950223165139, 4.5441785290796535, 4.936111098825381, 5.121433202528152
#     ],
#     "S19": [
#         0.7052617211701453, 1.3458463683636666, 2.2380301061767103, 3.1880115002581118, 3.9176526926703947
#     ],
# }

# data_from = sessions["S1"]  
# data_to = sessions["S2"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S1-S2: {statistic}, P-Value: {p_value}")

# data_from = sessions["S2"]  
# data_to = sessions["S3"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S2-S3: {statistic}, P-Value: {p_value}")

# data_from = sessions["S3"]  
# data_to = sessions["S4"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S3-S4: {statistic}, P-Value: {p_value}")

# data_from = sessions["S4"]  
# data_to = sessions["S5"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S4-S5: {statistic}, P-Value: {p_value}")

# data_from = sessions["S5"]  
# data_to = sessions["S6"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S5-S6: {statistic}, P-Value: {p_value}")

# data_from = sessions["S6"]  
# data_to = sessions["S7"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S6-S7: {statistic}, P-Value: {p_value}")

# data_from = sessions["S7"]  
# data_to = sessions["S8"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S7-S8: {statistic}, P-Value: {p_value}")

# data_from = sessions["S8"]  
# data_to = sessions["S9"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S8-S9: {statistic}, P-Value: {p_value}")

# data_from = sessions["S9"]  
# data_to = sessions["S10"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S9-S10: {statistic}, P-Value: {p_value}")

# data_from = sessions["S10"]  
# data_to = sessions["S11"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S10-S11: {statistic}, P-Value: {p_value}")

# data_from = sessions["S11"]  
# data_to = sessions["S12"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S11-S12: {statistic}, P-Value: {p_value}")

# data_from = sessions["S12"]  
# data_to = sessions["S13"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S12-S13: {statistic}, P-Value: {p_value}")

# data_from = sessions["S13"]  
# data_to = sessions["S14"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S13-S14: {statistic}, P-Value: {p_value}")

# data_from = sessions["S14"]  
# data_to = sessions["S15"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S14-S15: {statistic}, P-Value: {p_value}")

# data_from = sessions["S15"]  
# data_to = sessions["S16"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S15-S16: {statistic}, P-Value: {p_value}")

# data_from = sessions["S16"]  
# data_to = sessions["S17"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S16-S17: {statistic}, P-Value: {p_value}")

# data_from = sessions["S17"]  
# data_to = sessions["S18"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S17-S18: {statistic}, P-Value: {p_value}")

# data_from = sessions["S18"]  
# data_to = sessions["S19"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S18-S19: {statistic}, P-Value: {p_value}")


# data_from = sessions["S1"]  
# data_to = sessions["S19"]    
# statistic, p_value = Wilcoxon(data_from, data_to)
# print(f"Statistic S1-S19: {statistic}, P-Value: {p_value}")

# for session, wc_values in sessions.items():
#     print(f"{session}= {wc_values};")
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
