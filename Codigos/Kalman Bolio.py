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

def observation_matrices(m_all, m_significant, m_non_significant):
    """
    This function returns the observation matrices for a given number of sensors 
    (m_all), significant sensors (m_significant), and non-significant sensors 
    (m_non_significant).

    Parameters:
        - m_all (int): The total number of sensors.
        - m_significant (int): The number of significant sensors.
        - m_non_significant (int): The number of non-significant sensors.

    It does so by: 
        1.- Creating an identity matrix of size m_all x m_all.
        2.- Creating a zero matrix of size m_significant x m_all.
        3.- Creating a zero matrix of size m_non_significant x m_all.
        4.- Filling the last three columns of the H_significant matrix with 1s 
        to take into account the three significant sensors.
        5.- Filling the diagonal of the H_non_significant matrix with 1s to take 
        into account the non-significant sensors.

    Returns:
        - H_all (numpy.ndarray): The identity matrix of size m_all x m_all.
        - H_significant (numpy.ndarray): The significant observation matrix of 
        size m_significant x m_all.
        - H_non_significant (numpy.ndarray): The non-significant observation 
        matrix of size m_non_significant x m_all.
    """
    H_all = np.identity(m_all)
    H_significant = np.zeros(m_significant, m_all)
    H_non_significant = np.zeros(m_non_significant, m_all)

    H_significant[0, -3] = 1
    H_significant[1, -2] = 1
    H_significant[2, -1] = 1

    for i in range(m_non_significant):
        H_non_significant[i, i] = 1

    return H_all, H_significant, H_non_significant

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

    It does so by:
    1.- Using the ldl function from the scipy.linalg module to perform the LDL 
    decomposition of P.
    2.- Storing the lower triangular matrix of the decomposition in S.

    Returns:
    S (numpy.ndarray): The lower triangular matrix of the decomposition.
    """
    L, D, perm = ldl(P)
    S = L @ sqrtm(D)
    return S

def givens_rotation(F, Q, S):
  """
  This function performs a Givens rotation on the matrix U to zero out the 
  elements below the diagonal and ultimately output the upper triangular matrix.

  Parameters:
  F (numpy.ndarray): The state transition matrix.
  Q (numpy.ndarray): The process noise covariance matrix.
  S (numpy.ndarray): The measurement noise covariance matrix.

  It does so by:
  1.- Concatenating the product of F.T and S.T with Q.T.
  2.- Looping through the matrix to perform the Givens rotation.
  3.- Storing the upper triangular matrix of the decomposition in S.

  Returns:
  S (numpy.ndarray): The upper triangular matrix of the decomposition.
  """
  m = S.shape[0]
  U = np.concatenate([F.T @ S.T, np.sqrt(Q.T)], axis=0)

  for j in range(m):
    for i in range(2 * m - 1, j, -1):
      B = np.eye(2 * m)
      a = U[i-1, j]
      b = U[i, j]

      if b == 0:
        c = 1
        s = 0
      elif abs(b) > abs(a):
        r = a/b
        s = 1/np.sqrt(1 + r**2)
        c = s * r
      else:
        r = b/a
        c = 1/np.sqrt(1 + r**2)
        s = c * r

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
      U = np.dot(B.T, U)

  S = U[:m, :m]
  return S

def potter(x_t_p, S_t_p, y_t, H, R, I):
    x_i = x_t_p
    S_i = S_t_p
    n = y_t.shape[0]

    phi_i = np.zeros((14, 1))

    for i in range(n):
        H_i = H[i]
        y_i = y_t[i].item()
        R_i = np.var(R[i])

        phi_i = S_i.T @ H_i.T
        alpha_i = 1 / (phi_i.T @ phi_i + R_i)
        gamma_i = alpha_i / (1 + math.sqrt(alpha_i * R_i))

        S_i = S_i @ (np.eye(n) - alpha_i * gamma_i * (phi_i @ phi_i.T))
        K_i = S_i @ phi_i
        x_i = x_i + K_i * (y_i - phi_i.T @ x_i)

    return x_i, S_i


def kalmanEnsemble(X, H):
    results = []

    x = np.zeros((14, 1))

    x = X[0]

    P = process_covariance_matrix(X)
    S = ldl_decomposition(P)
    S = S.T

    F = taylor_series(len(x))

    # First iteration
    w = np.random.normal(size=(len(x)))

    Q = np.identity(len(x)) * np.std(w)

    xp = F @ x + w

    Sp = givens_rotation(F, Q, S)

    z = np.random.normal(size=(len(H)))
    R = np.identity(len(x)) * np.std(z)

    y_t = H @ x + z
    x_prev, S_prev = potter(xp, Sp, y_t, H, R)

    results.append(x_prev)

    for i in range(1, len(X)):
        w = np.random.normal(size=(len(x)))
        Q = np.identity(len(x)) * np.std(w)

        xp = F @ x_prev + w
        Sp = givens_rotation(F, Q, S_prev)
        z = np.random.normal(size=(len(H)))

        R = np.identity(len(H)) * np.std(z)

        y_t = H @ x + z

        x_prev, S_prev = potter(xp, Sp, y_t, H, R)

        results.append(x_prev)

    return results

results = kalmanEnsemble(dataUser1.iloc[:, :14], )

# time = range(len(dataUser1))  
# sensor_labels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

# meaningful_sensors = ['F4', 'F8', 'AF4']
# kalman_data = dataUser1.rolling(window=5).mean()

# fig, axs = plt.subplots(3, 1, figsize=(10, 15))  

# for i, label in enumerate(meaningful_sensors):
#     sensor_data = dataUser1[label]
#     axs[i].plot(time, sensor_data, color='lightsteelblue')
#     axs[i].set_title(f'Sensor {label}: Comparacion de Señal Original y Filtrada')
#     axs[i].set_xlabel('Time')
#     axs[i].set_ylabel('Sensor Reading')
#     axs[i].set_facecolor('slategray')
#     axs[i].grid(True, color='darkslategray')

# plt.tight_layout()
# plt.show()

# fig, axs = plt.subplots(3, 1, figsize=(10, 15))  
# for i, label in enumerate(meaningful_sensors):
#     sensor_data = dataUser1[label] 
#     kalman_sensor_data = kalman_data[label]   
#     axs[i].plot(time, sensor_data, label=f'Original {label}', color='lightsteelblue')
#     axs[i].plot(time, kalman_sensor_data, label=f'Kalman {label}', color='lime')  
#     axs[i].set_title(f'Sensor {label}')
#     axs[i].set_xlabel('Time')
#     axs[i].set_ylabel('Sensor Reading')
#     axs[i].set_facecolor('slategray')
#     axs[i].grid(True, color='darkslategray')
#     axs[i].legend()

# plt.suptitle('Comparacion de Señal Original y Filtrada con Filtro de Kalman', fontsize=16)
# plt.tight_layout()
# plt.show()
