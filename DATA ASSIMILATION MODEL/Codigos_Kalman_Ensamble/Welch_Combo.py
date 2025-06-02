#!/usr/bin/env python3
import os
import numpy as np
from scipy.signal import welch

def Welch(signal, fs=128, nperseg=128):
    f, Pxx = welch(signal, fs=fs, nperseg=nperseg)
    return f, 10*np.log10(Pxx)

# --- RUTAS BASE -------------------------------------------------------------
input_base  = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/PROCESSED_KALMAN')
output_base = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/WELCH')
os.makedirs(output_base, exist_ok=True)

# --- CONFIGURACIÓN ----------------------------------------------------------
users = ['Karen', 'Omar', 'Rafael', 'Ruben', 'David', 'Eveline', 'Luis']

session_ranges = {
    'Karen':   range(1, 19),
    'David':   range(2, 11),
    'Ruben':   range(1, 8),
    'Omar':    range(2, 20),
    'Rafael':  range(2, 20),
    'Eveline': range(2, 20),
    'Luis':    range(2, 20),
}

mod_labels = [
    'Potter_GramSchmidt',   'Carlson_GramSchmidt',  'Bierman_GramSchmidt',
    'Potter_Givens',        'Carlson_Givens',       'Bierman_Givens',
    'Potter_Householder',   'Carlson_Householder',  'Bierman_Householder',
]

labels = ["All", "NWC", "Original", "WC"]

# ---------------------------------------------------------------------------
def get_sessions(user):
    return [f"S{s}" for s in session_ranges.get(user, range(1, 20))]

for user in users:
    user_dir = os.path.join(input_base, f"PROCESSED_KALMAN_{user.upper()}")
    if not os.path.isdir(user_dir):
        print(f"[WARN] No se encontró la carpeta del usuario: {user_dir}.  Se omite {user}.")
        continue

    user_out = os.path.join(output_base, f"WELCH_{user.upper()}")
    os.makedirs(user_out, exist_ok=True)

    for mod in mod_labels:
        meth, orth = (mod.split('_', 1) + [""])[:2]
        mod_out = os.path.join(user_out, f"Kalman_{orth}_{meth}")
        os.makedirs(mod_out, exist_ok=True)

        for sess in get_sessions(user):
            print(f"[{user} | {mod}]  Sesión {sess}")

            session_data, freqs = {}, None

            for lab in labels:
                amp_file = f"{sess}_{mod}_amplitude_{lab}.csv"
                amp_path = os.path.join(user_dir, sess, amp_file)   # <- subdir de la sesión

                if os.path.exists(amp_path):
                    sig = np.loadtxt(amp_path, delimiter=',')
                    f, Pxx = Welch(sig)
                    if freqs is None:
                        freqs = f
                    session_data[lab] = Pxx
                else:
                    if freqs is not None:
                        session_data[lab] = np.zeros_like(freqs)
                    else:
                        session_data[lab] = None
                    print(f"   · Falta {amp_file}  →  ceros/skipped")

            if freqs is None:
                print("   · Sin datos válidos → se omite la sesión completa")
                continue

            out_csv = os.path.join(mod_out, f"{sess}_welch.csv")
            with open(out_csv, "w") as fout:
                fout.write("Frequency," + ",".join(f"Power_{lab}" for lab in labels) + "\n")
                for i, fval in enumerate(freqs):
                    row = [fval] + [session_data[lab][i] if session_data[lab] is not None else 0.
                                    for lab in labels]
                    fout.write(",".join(map(str, row)) + "\n")

            print(f"   · Guardado  →  {out_csv}")

    print(f"--- Terminado el usuario {user} ---\n")

print("Proceso completado: todos los Welch generados.")
