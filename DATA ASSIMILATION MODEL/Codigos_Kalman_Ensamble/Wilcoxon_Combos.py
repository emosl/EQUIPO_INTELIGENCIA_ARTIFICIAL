#!/usr/bin/env python3
"""
Calcula la prueba de rangos con signo de Wilcoxon sobre la serie Power_WC
entre cada par de sesiones consecutivas (S1→S2, S2→S3, …, S18→S19, S19→S1)
para **cada usuario** y **cada variante Kalman**.

Estructura esperada de entrada (igual que el script de gráficas):

WELCH/
└── WELCH_<USER>/
    └── Kalman_<orth>_<method>/
        ├── S4_welch.csv
        └── …

Los resultados se guardan como

WILCOXON/
└── WILCOXON_<USER>/
    └── Kalman_<orth>_<method>_wilcoxon_wc.csv
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

# --- Rutas base -------------------------------------------------------------
input_root  = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/WELCH')
output_root = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/WILCOXON')
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

# ---------------------------------------------------------------------------
def wilcoxon_pair(col1, col2):
    """Devuelve (statistic, p_value) de Wilcoxon; si falla por valores iguales, devuelve (nan, 1)."""
    try:
        stat, p = wilcoxon(col1, col2)
    except ValueError:          # e.g., cuando todas las diferencias son 0
        stat, p = np.nan, 1.0
    return stat, p

# ---------------------------------------------------------------------------
for user in users:
    user_in = os.path.join(input_root, f"WELCH_{user.upper()}")
    if not os.path.isdir(user_in):
        print(f"[WARN] Falta WELCH_{user}: {user_in}")
        continue

    user_out = os.path.join(output_root, f"WILCOXON_{user.upper()}")
    os.makedirs(user_out, exist_ok=True)

    for mod in mod_labels:
        meth, orth = (mod.split('_', 1) + [""])[:2]
        mod_in  = os.path.join(user_in,  f"Kalman_{orth}_{meth}")
        if not os.path.isdir(mod_in):
            print(f"   · [WARN] Falta dir {mod_in} – se omite")
            continue

        # Reunir solo sesiones que realmente existen
        available = []
        for sess in get_sessions(user):
            csv_path = os.path.join(mod_in, f"{sess}_welch.csv")
            if os.path.exists(csv_path):
                available.append((sess, csv_path))

        if len(available) < 2:
            print(f"   · [INFO] Menos de 2 sesiones disponibles para {user} {mod}")
            continue

        # Ordenar por número de sesión
        available.sort(key=lambda t: int(t[0][1:]))

        # Wilcoxon entre consecutivas + wrap-around última→primera
        results = []
        pairs = [(available[i], available[i+1]) for i in range(len(available)-1)]
        pairs.append((available[-1], available[0]))  # cierre

        for (s_from, f_from), (s_to, f_to) in pairs:
            df_from = pd.read_csv(f_from)
            df_to   = pd.read_csv(f_to)

            col_from = df_from['Power_WC'].values
            col_to   = df_to['Power_WC'].values

            stat, p = wilcoxon_pair(col_from, col_to)
            results.append([s_from, s_to, stat, p])

        # Guardar CSV de resultados
        out_name = f"Kalman_{orth}_{meth}_wilcoxon_wc.csv"
        out_path = os.path.join(user_out, out_name)

        pd.DataFrame(results,
                     columns=['From_Session', 'To_Session', 'Statistic', 'P_Value']
                    ).to_csv(out_path, index=False)

        print(f"   · Wilcoxon guardado → {out_path}")

print("Proceso completo: archivos de Wilcoxon generados en WILCOXON/")
