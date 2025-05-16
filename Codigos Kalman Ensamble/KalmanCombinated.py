# test_all_kalman.py
import numpy as np
import time

import Kalman_GramShmidt_Potter as kpgs
import Kalman_GramShmidt_Carlson as kcgs
import Kalman_GramShmidt_Bierman as kgbgs

import Kalman_Givens_Potter as kpgv
import Kalman_Givens_Carlson as kcg
import Kalman_Givens_Bierman as kgbgv

import Kalman_Householder_Potter as kphp
import Kalman_Householder_Carlson as khc
import Kalman_Householder_Bierman as khb

if __name__ == '__main__':
    file_path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN/S1.csv'
    Fs = 128
    wC = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])

    modules = [
        ('Potter_GramSchmidt', kpgs.run),
        ('Carlson_GramSchmidt', kcgs.run),
        ('Bierman_GramSchmidt', kgbgs.run),
        ('Potter_Givens', kpgv.run),
        ('Carlson_Givens', kcg.run),
        ('Bierman_Givens', kgbgv.run),
        ('Potter_Householder', kphp.run),
        ('Carlson_Householder', khc.run),
        ('Bierman_Householder', khb.run)
    ]

    times = {}
    for name, func in modules:
        start = time.time()
        _ = func(file_path, Fs, wC)
        times[name] = time.time() - start

    with open('kalman_execution_times.txt', 'w') as f:
        for name, t in times.items():
            f.write(f"{name}: {t}\n")

    print('Execution times saved to kalman_execution_times.txt')
