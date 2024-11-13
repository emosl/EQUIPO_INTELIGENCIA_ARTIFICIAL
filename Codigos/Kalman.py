import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
from scipy.linalg import ldl
import math


dataUser1 = pd.read_csv('SEGUNDO_BLOQUE/LIZ/KALMAN EN ENSAMBLE/Kalman Ensemble.csv')
dataUser1.columns = dataUser1.columns.str.strip()


Fs = 128
m = 14
process_noise_std = 1e-2
measurement_noise_std = 1e-1


def taylor_series_P(Fs, m):
    delta_t = 1 / Fs
    P = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            P[i, j] = (delta_t ** (abs(j - i))) / math.factorial(abs(j - i))
    return P

def transition_matrix_F(P, process_noise_std):
    w = np.random.normal(0, process_noise_std, P.shape)
    F = P + w  
    return F

def LDL_T(F):
    L, D, perm = ldl(F)
    return L, D, L.T

def Givens(U):
    rows, cols = U.shape
    for j in range(cols):
        for i in range(rows - 1, j, -1):
            a = U[i - 1, j]
            b = U[i, j]
            if b == 0:
                c, s = 1, 0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s = 1 / np.sqrt(1 + r**2)
                    c = s * r
                else:
                    r = b / a
                    c = 1 / np.sqrt(1 + r**2)
                    s = c * r

            B = np.identity(rows)
            B[i - 1, i - 1], B[i - 1, i], B[i, i - 1], B[i, i] = c, s, -s, c
            U = np.dot(B, U)
    return U

def Potter(x_p_t, S_p_t, y_t, H, R, I):
    x_t = x_p_t
    S_t = S_p_t
    n = len(y_t)
    for i in range(n):
        H_i = H[i, :]
        y_i_t = y_t[i]
        R_i = R[i, i]
        Phi_i = np.dot(S_t.T, H_i.T)
        a_i = 1 / (np.dot(Phi_i.T, Phi_i) + R_i)
        gamma_i = a_i / (1 + np.sqrt(a_i * R_i))
        S_t = S_t * (I - a_i * gamma_i * np.dot(Phi_i, Phi_i.T))
        K_i_t = np.dot(S_t, Phi_i)
        x_t = x_t + K_i_t * (y_i_t - np.dot(H_i, x_t))
    return x_t, S_t


def EnKF(data, Fs, m, process_noise_std, measurement_noise_std):
    P = taylor_series_P(Fs, m)
    F = transition_matrix_F(P, process_noise_std)
    L, D, LT = LDL_T(F)
    S = Givens(np.dot(np.dot(L, D), LT))
    x_p_t = np.zeros(m)  
    S_p_t = S
    
    y_t = data.iloc[0].values[:m]  
    H = np.identity(m)  
    R = np.identity(m) * measurement_noise_std  
    I = np.identity(m)  

    x_t, S_t = Potter(x_p_t, S_p_t, y_t, H, R, I)

    return x_t, S_t


x_t, S_t = EnKF(dataUser1, Fs, m, process_noise_std, measurement_noise_std)



time = range(len(dataUser1))  
sensor_labels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

meaningful_sensors = ['F4', 'F8', 'AF4']
kalman_data = dataUser1.rolling(window=5).mean()

fig, axs = plt.subplots(3, 1, figsize=(10, 15))  

for i, label in enumerate(meaningful_sensors):
    sensor_data = dataUser1[label]
    axs[i].plot(time, sensor_data, color='lightsteelblue')
    axs[i].set_title(f'Sensor {label}: Comparacion de Señal Original y Filtrada')
    axs[i].set_xlabel('Time')
    axs[i].set_ylabel('Sensor Reading')
    axs[i].set_facecolor('slategray')
    axs[i].grid(True, color='darkslategray')

plt.tight_layout()
plt.show()

fig, axs = plt.subplots(3, 1, figsize=(10, 15))  
for i, label in enumerate(meaningful_sensors):
    sensor_data = dataUser1[label] 
    kalman_sensor_data = kalman_data[label]   
    axs[i].plot(time, sensor_data, label=f'Original {label}', color='lightsteelblue')
    axs[i].plot(time, kalman_sensor_data, label=f'Kalman {label}', color='lime')  
    axs[i].set_title(f'Sensor {label}')
    axs[i].set_xlabel('Time')
    axs[i].set_ylabel('Sensor Reading')
    axs[i].set_facecolor('slategray')
    axs[i].grid(True, color='darkslategray')
    axs[i].legend()

plt.suptitle('Comparacion de Señal Original y Filtrada con Filtro de Kalman', fontsize=16)
plt.tight_layout()
plt.show()
