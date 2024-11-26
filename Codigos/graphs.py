import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Input and output file paths
input_file = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/WILCOXON/wilcoxon_wc_results.csv'
output_file = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/GRAFICAS/wilcoxon_p_values_log_plot.png'

# Read the CSV file
data = pd.read_csv(input_file)

# Extract data for plotting
labels = [f"{row['From_Session']}-{row['To_Session']}" for _, row in data.iterrows()]
p_values = data['P_Value']

# Avoid errors with log(0) by adding a small epsilon to p-values
epsilon = 1e-12
p_values_log = np.log10(p_values + epsilon)

# Create the plot
plt.figure(figsize=(10, 6))
plt.scatter(range(len(p_values)), p_values_log, color='blue', label='Log10(P-Values)', zorder=2)
plt.axhline(np.log10(0.05), color='red', linestyle='--', label='Threshold (0.05)', zorder=1)
plt.xticks(range(len(p_values)), labels, rotation=45, ha='right')
plt.xlabel('Session Transitions', fontsize=12)
plt.ylabel('Log10(P-Value)', fontsize=12)
plt.title('Log-Scaled Wilcoxon P-Values for Session Transitions', fontsize=14)
plt.legend()
plt.grid(zorder=0)

# Save the plot
plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.close()

print(f"Log-scaled plot saved to {output_file}")
