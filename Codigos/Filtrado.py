import pandas as pd
import numpy as np

columns_to_use = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
column_names = ['COUNTER', 'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']


data = pd.read_csv(
    '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/INTELIGENCIA_ARTIFICIAL/SEGUNDO_BLOQUE/LIZ/FILTRADO1/Cognitiv Anakaren Session 12.csv',
    usecols=columns_to_use,
    names=column_names,
    header=0,  
    skipinitialspace=True
)

filtered_data = data.iloc[:, 1:]  
final_tensor = []
chunk_size = 128
not_addes = []
not_added_seconds = []
messages = []  

i = 0  
processed_seconds = set()  


while i < filtered_data.shape[0]:
    if data.iloc[i, 0] == 0:  
        if i + chunk_size <= filtered_data.shape[0]:  
            chunk = data.iloc[i:i + chunk_size]
            duplicate_rows = chunk.duplicated(keep='first')
            if duplicate_rows.any():
                messages.append("Duplicate rows found and removed based on all columns.")
                chunk = chunk[~duplicate_rows]
                
                extra_index = i + chunk_size
                while len(chunk) < chunk_size and extra_index < filtered_data.shape[0]:
                    next_row = data.iloc[extra_index]
                    if not next_row.equals(chunk.iloc[-1]): 
                        chunk = pd.concat([chunk, next_row.to_frame().T], ignore_index=True)
                    extra_index += 1

            counter_values = chunk['COUNTER'].values
            current_second = i // 128
            if len(counter_values) == chunk_size and counter_values[0] == 0 and counter_values[-1] == 127:
                final_tensor.append(chunk.iloc[:, 1:].values)  
            else:
                if current_second not in processed_seconds:  
                    messages.append(f"NOT ADDED {current_second}")
                    messages.append(f"Pattern mismatch at index {i}. First COUNTER value: {counter_values[0]}, Last COUNTER value: {counter_values[-1]}")
                    messages.append(f"Values after removing exact duplicates and filling: {counter_values}")
                    messages.append(f"Values shape: {len(counter_values)}")
                    not_addes.append(counter_values)
                    not_added_seconds.append(current_second)
                    processed_seconds.add(current_second) 
        
        i += 1  
    else:
        i += 1  

tensor = np.array(final_tensor)
messages.append(f"Final tensor shape: {tensor.shape}")


for message in messages:
    print(message)

"""
for idx, not_added_time in enumerate(not_added_seconds):
    timestamp = not_added_time
    print(f"Block not added at second: {timestamp}")
    print("COUNTER values in the block:", not_addes[idx])

"""



print("NOT ADDED SECONDS", not_added_seconds)
differences = [not_added_seconds[i+1] - not_added_seconds[i] for i in range(len(not_added_seconds) - 1)]

max_difference = max(differences)
index_of_max_difference = differences.index(max_difference)

start_second = not_added_seconds[index_of_max_difference]
end_second = not_added_seconds[index_of_max_difference + 1]

print(f"The longest interval is {max_difference} seconds, between {start_second} and {end_second}.")