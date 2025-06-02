#!/usr/bin/env python3
"""
Crea un PNG por cada archivo *_welch.csv generado previamente:

WELCH/
└── WELCH_<USER>/
    └── Kalman_<orth>_<method>/
        ├── S4_welch.csv        →  S4_plot.png
        └── …

Las gráficas se guardan con la misma jerarquía bajo WELCH_PLOTS/.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

# --- Rutas base -------------------------------------------------------------
input_root  = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/WELCH')
output_root = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/WELCH_PLOTS')
os.makedirs(output_root, exist_ok=True)

# --- Configuración idéntica a los scripts previos ---------------------------
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

def get_sessions(user):
    return [f"S{s}" for s in session_ranges.get(user, range(1, 20))]

mod_labels = [
    'Potter_GramSchmidt',   'Carlson_GramSchmidt',  'Bierman_GramSchmidt',
    'Potter_Givens',        'Carlson_Givens',       'Bierman_Givens',
    'Potter_Householder',   'Carlson_Householder',  'Bierman_Householder',
]

plot_headers = ["Power_All", "Power_Original", "Power_WC", "Power_NWC"]
colors  = {"Power_All": "red", "Power_Original": "blue",
           "Power_WC": "green", "Power_NWC": "black"}
markers = {"Power_All": "o",   "Power_Original": "s",
           "Power_WC": "^",    "Power_NWC": "x"}

# --- Función de graficado ---------------------------------------------------
def plot_welch(csv_path, save_path, title_txt):
    data  = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    freqs = data[:, 0]

    plt.figure(figsize=(10, 6))
    plt.title(title_txt, fontsize=16)
    plt.xlabel("Frequency (Hz)", fontsize=14)
    plt.ylabel("Power Spectral Density (dB)", fontsize=14)
    plt.grid(True)

    for idx, hdr in enumerate(plot_headers, start=1):
        plt.plot(freqs,
                 data[:, idx],
                 label=hdr.replace("Power_", ""),
                 color=colors[hdr],
                 marker=markers[hdr],
                 markersize=4,
                 linewidth=1.3)

    plt.legend(title="Amplitude Type", fontsize=11)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

# --- Bucle principal --------------------------------------------------------
for user in users:
    user_in  = os.path.join(input_root, f"WELCH_{user.upper()}")
    if not os.path.isdir(user_in):
        print(f"[WARN] Carpeta faltante para {user}: {user_in}")
        continue

    user_out = os.path.join(output_root, f"WELCH_{user.upper()}")
    os.makedirs(user_out, exist_ok=True)

    for mod in mod_labels:
        meth, orth = (mod.split('_', 1) + [""])[:2]
        mod_in  = os.path.join(user_in,  f"Kalman_{orth}_{meth}")
        if not os.path.isdir(mod_in):
            print(f"   · [WARN] Falta dir {mod_in} – se omite")
            continue

        mod_out = os.path.join(user_out, f"Kalman_{orth}_{meth}")
        os.makedirs(mod_out, exist_ok=True)

        for sess in get_sessions(user):
            csv_name = f"{sess}_welch.csv"
            csv_path = os.path.join(mod_in, csv_name)
            if not os.path.exists(csv_path):
                print(f"   · [INFO] No existe {csv_name}")
                continue

            png_name = f"{sess}_plot.png"
            png_path = os.path.join(mod_out, png_name)
            title    = f"{sess} – {user} – {meth}/{orth}"

            print(f"[{user} | {mod}]  {sess} → plotting")
            plot_welch(csv_path, png_path, title)
            print(f"   · Guardado → {png_path}")

print("Listo: todas las gráficas fueron generadas en WELCH_PLOTS/")
