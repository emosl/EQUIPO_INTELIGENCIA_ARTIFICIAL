#!/usr/bin/env python3
import os
import time
import numpy as np
import Kalman_GramShmidt_Potter as kpgs
import Kalman_GramShmidt_Carlson as kcgs
import Kalman_GramShmidt_Bierman as kgbgs
import Kalman_Givens_Potter as kpgv
import Kalman_Givens_Carlson as kcg
import Kalman_Givens_Bierman as kgbgv
import Kalman_Householder_Potter as kphp
import Kalman_Householder_Carlson as khc
import Kalman_Householder_Bierman as khb

# Significant-sensor masks for each user
wC_users = {
    'Karen':   np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1]),
    'Omar':    np.array([0,0,1,1,0,0,0,0,0,0,0,1,1,1]),
    'Rafael':  np.array([0,0,0,1,0,0,0,0,0,1,0,1,1,1]),
    'Ruben':   np.array([0,0,0,0,0,0,0,0,1,0,0,1,0,1]),
    'David':   np.array([0,0,0,0,0,0,0,0,0,1,0,0,1,1]),
    'Eveline': np.array([0,0,1,0,0,0,0,0,0,0,1,0,0,1]),
    'Luis':    np.array([0,0,0,1,0,0,0,0,0,0,0,1,0,1]),
}

# Kalman variants
modules = [
    ('Potter_GramSchmidt', kpgs.run),
    ('Carlson_GramSchmidt', kcgs.run),
    ('Bierman_GramSchmidt', kgbgs.run),
    ('Potter_Givens',      kpgv.run),
    ('Carlson_Givens',     kcg.run),
    ('Bierman_Givens',     kgbgv.run),
    ('Potter_Householder', kphp.run),
    ('Carlson_Householder', khc.run),
    ('Bierman_Householder', khb.run),
]

Fs = 128  # sampling rate

root_input_dir  = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN'
root_output_dir = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN'
exec_times_dir  = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/EXCECUTION_TIMES'

os.makedirs(exec_times_dir, exist_ok=True)

times = []
failures = []

# Define session ranges per user
session_ranges = {
    'Karen':  range(1, 20),
    'David':  range(2, 11),
    'Ruben':  range(1, 8),
    'Omar':   range(1, 20),
    'Rafael': range(1, 20),
    'Eveline': range(1, 20),
    'Luis':   range(1, 20),

}
def get_sessions(user):
    return session_ranges.get(user, range(2, 20))

for user_name, wC in wC_users.items():
    input_folder  = os.path.join(root_input_dir,  f'KALMAN_{user_name}')
    output_folder = os.path.join(root_output_dir, f'PROCESSED_KALMAN_{user_name.upper()}')
    os.makedirs(output_folder, exist_ok=True)

    for sess in get_sessions(user_name):
        session_name = f'S{sess}'
        file_path = os.path.join(input_folder, f'{session_name}.csv')

        for mod_label, func in modules:
            key = f"{user_name}_{session_name}_{mod_label}"
            start = time.time()
            try:
                # expect run() to return: All, Original, WC, NWC, yAll, yWC, yNWC
                allRes, origRes, wcRes, nwcRes, yAll, yWC, yNWC = func(file_path, Fs, wC)
                elapsed = time.time() - start
                times.append((key, elapsed))

                # flatten amplitudes
                amps = {
                    'All':      np.concatenate(allRes),
                    'Original': np.concatenate(origRes),
                    'WC':       np.concatenate(wcRes),
                    'NWC':      np.concatenate(nwcRes),
                }
                ys = {
                    'All': np.array(yAll),
                    'WC':  np.array(yWC),
                    'NWC': np.array(yNWC),
                }

                # save amplitude series
                for suffix, amp in amps.items():
                    out_amp = os.path.join(
                        output_folder,
                        f"{session_name}_{mod_label}_amplitude_{suffix}.csv"
                    )
                    np.savetxt(out_amp, amp, delimiter=',')

                # save measurement series
                for suffix, y in ys.items():
                    out_y = os.path.join(
                        output_folder,
                        f"{session_name}_{mod_label}_y_{suffix}.csv"
                    )
                    np.savetxt(out_y, y, delimiter=',')

                print(f"{session_name}_{mod_label} saved.")

            except Exception as e:
                print(f"Error occurred running Kalman for {user_name} {session_name} {mod_label}: {e}")
                failures.append(key)
                continue

    # write this user's execution times
    user_times_file = os.path.join(exec_times_dir, f"{user_name}_execution_times.txt")
    with open(user_times_file, 'w') as f:
        for key, t in times:
            if key.startswith(user_name + '_'):
                f.write(f"{key}: {t:.3f}s\n")

# write global execution times
global_times_file = os.path.join(exec_times_dir, 'kalman_execution_times.txt')
with open(global_times_file, 'w') as f:
    for key, t in times:
        f.write(f"{key}: {t:.3f}s\n")

# write failures to separate file
failures_file = os.path.join(exec_times_dir, 'failed_runs.txt')
with open(failures_file, 'w') as f:
    for key in failures:
        f.write(f"{key}\n")

print("Processing complete for all users and sessions.")
