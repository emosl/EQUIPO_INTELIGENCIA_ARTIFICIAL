#!/usr/bin/env python3
"""
Genera una única gráfica por combinación Kalman para la sesión S3:
• Curva "Original" vs. curva "Predicted (All)".

Además calcula la RMSE entre ambas y la guarda en un CSV.
Las figuras se escriben en …/GRAFICAS/S3/<Usuario>/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------ Rutas base ----------------------------------------------------
root_kalman = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
               'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/PROCESSED_KALMAN')

out_root = ('/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/'
            'EQUIPO_INTELIGENCIA_ARTIFICIAL/DATA ASSIMILATION MODEL/GRAFICAS/S3')
os.makedirs(out_root, exist_ok=True)

# ------------ Configuración -------------------------------------------------
users = ['Karen', 'Omar', 'Rafael', 'Ruben', 'David', 'Eveline', 'Luis']
mod_labels = [
    'Potter_GramSchmidt',   'Carlson_GramSchmidt',  'Bierman_GramSchmidt',
    'Potter_Givens',        'Carlson_Givens',       'Bierman_Givens',
    'Potter_Householder',   'Carlson_Householder',  'Bierman_Householder',
]
SESSION = "S3"              # Cambia aquí si quieres otra sesión

# ------------ Helpers -------------------------------------------------------
def load_amp(user, session, mod, suffix):
    file_name = f"{session}_{mod}_amplitude_{suffix}.csv"
    path = os.path.join(root_kalman,
                        f"PROCESSED_KALMAN_{user.upper()}",
                        session,
                        file_name)
    return np.loadtxt(path, delimiter=',') if os.path.exists(path) else None

def rmse(a, b):
    return np.sqrt(np.mean((a - b) ** 2))

# ------------ Bucle principal ----------------------------------------------
metrics = []

for user in users:
    user_out = os.path.join(out_root, user)
    os.makedirs(user_out, exist_ok=True)

    for mod in mod_labels:
        orig = load_amp(user, SESSION, mod, "Original")
        pred = load_amp(user, SESSION, mod, "All")

        if orig is None or pred is None:
            print(f"[WARN] Faltan datos para {user} – {mod}. Se omite.")
            continue

        t = np.arange(len(orig))

        # ----- Gráfica -----------------------------------------------------
        plt.figure(figsize=(12, 5))
        plt.plot(t, orig, label="Original", color="black", linewidth=1)
        plt.plot(t, pred, label="Predicted (All)", color="magenta", alpha=0.6)
        plt.title(f"{user} – {mod} – {SESSION}\nOriginal vs Predicted")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.tight_layout()

        fig_path = os.path.join(user_out, f"{SESSION}_{mod}_orig_vs_pred.png")
        plt.savefig(fig_path, dpi=300)
        plt.close()

        # ----- Métrica -----------------------------------------------------
        metrics.append({
            "User": user,
            "Kalman": mod,
            "RMSE_Orig_All": rmse(orig, pred)
        })

        print(f"✔ Gráfico guardado → {fig_path}")

# ------------ Guardar CSV de métricas --------------------------------------
pd.DataFrame(metrics).to_csv(
    os.path.join(out_root, f"rmse_{SESSION}.csv"), index=False
)

print("\nProceso finalizado: gráficos y métricas generados.")
