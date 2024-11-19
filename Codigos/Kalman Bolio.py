import os
import math
import numpy as np
import pandas as pd
from scipy.linalg import ldl, sqrtm
import matplotlib.pyplot as plt

current_path = os.path.dirname(__file__) # Get the directory of the current script
file_path = '../ProcesadoMatlab/S1_matlab.csv' # Replace with the path to your CSV file
rel_path = os.path.join(current_path, file_path) # The relative path to the CSV file to plot

dataUser1 = pd.read_csv(rel_path) # Read the CSV file
dataUser1.columns = dataUser1.columns.str.strip()


Fs = 128 # Sampling frequency
m = 14 # Number of sensors
process_noise_std = 1e-2 
measurement_noise_std = 1e-1

def taylor_series(m, Fs=128):
    """
    This function returns the taylor series matrix or state transition matrix 
    for a given number of sensors (m) and sampling frequency (Fs)

    Parameters:
        - m (int): The number of sensors.
        - Fs (int): The sampling frequency.

    It does so by: 
        1.- Creating an identity matrix of size m x m.
        2.- Creating a tuple oneLoc that stores the location of the one in the 
        identity matrix.
        3.- Looping through the matrix to fill only the upper triangle with the 
        taylor series values.

    Returns:
        - F (numpy.ndarray): The state transition matrix.
    """
    deltaT = 1 / Fs
    F = np.identity(m)
    oneLoc = ()

    for i in range(m):
        for j in range(m):
            if F[i, j] == 1:
                oneLoc = (i, j)

            if i != j and j > i:
                k = j - oneLoc[1]
                F[i, j] = (deltaT ** k) / np.math.factorial(k)

    return F

def process_covariance_matrix(data):
    """
    This function calculates the process covariance matrix P for a given dataset.

    Parameters:
        - data (pandas.DataFrame): The dataset containing the sensor data.

    It does so by:
        1.- Getting the shape of the data and storing the number of columns in m.
        2.- Creating a zero matrix of size m x m.
        3.- Looping through the columns of the data:
            3.1.- If the current element in the matrix is a diagonal element,
            calculate the variance of the column and store it in the diagonal 
            element P[i, i].
            3.2.- If the current element in the matrix is not a diagonal element, 
            calculate the covariance between the current column and the previous    
            column and store it in the corresponding off-diagonal element of P.

    Returns:
        - P (numpy.ndarray): The process covariance matrix.
    """
    m = data.shape[1]
    P = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            if i == j:
                sigma_a = data.iloc[:, i] - np.mean(data.iloc[:, i])
                P[i, j] = np.sum((sigma_a ** 2) / len(data))
            else:
                sigma_a = data.iloc[:, i] - np.mean(data.iloc[:, i])
                sigma_b = data.iloc[:, j] - np.mean(data.iloc[:, j])
                P[i, j] = np.sum((sigma_a * sigma_b) / len(data))
    return P

def ldl_decomposition(P):
    """
    This function performs the LDL decomposition of a given matrix P and 
    produces an S matrix from it.

    Parameters:
    P (numpy.ndarray): The process covariance matrix to be decomposed.

    Returns:
    S (numpy.ndarray): The upper triangular matrix of the decomposition.
    """
    L, D, perm = ldl(P)
    S = L @ sqrtm(D)
    return S.T

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
            B[i - 1, i - 1] = c 
            B[i, i] = c
            B[i - 1, i] = s
            B[i, i - 1] = -s 
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


def EnKF(data, Fs, m, measurement_noise_std):
    P = process_covariance_matrix(data)
    F = taylor_series(m, Fs)
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
