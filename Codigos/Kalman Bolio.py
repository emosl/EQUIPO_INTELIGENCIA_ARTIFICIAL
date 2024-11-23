import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.linalg import ldl, sqrtm
from numpy.linalg import cholesky, solve

current_path = os.path.dirname(__file__) # Get the directory of the current script
file_path = '../ProcesadoMatlab/S1_matlab.csv' # Replace with the path to your CSV file
rel_path = os.path.join(current_path, file_path) # The relative path to the CSV file to plot

X = np.genfromtxt('User1_Pre2.csv', delimiter=',', skip_header=1) # Read the CSV file
sensors = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'] # The names of the sensors

Fs = 128 # Sampling frequency
m = 14 # Number of sensors
m_significant = 3 # Number of significant sensors [F4, F8, AF4]
m_non_significant = 11 # Number of non-significant sensors [AF7, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6]

def observation_matrices(m_all, m_significant, m_non_significant):
    """
    This function returns the observation matrices for a given number of sensors
    be that all sensors (m_all), significant sensors which are F4, F8 and AF4
    (m_significant), and non-significant sensors (m_non_significant).

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
    H_significant = np.zeros((m_significant, m_all))
    H_non_significant = np.zeros((m_non_significant, m_all))

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

    for i in range(m):
        for j in range(m):
            if i < j:
                k = j - i
                F[i, j] = (deltaT ** k) / math.factorial(k)

    return F

def ldl_decomposition(P):
    """
    This function performs the LDL decomposition of a given matrix P and
    produces an S matrix from it.

    Parameters:
        - P (numpy.ndarray): The process covariance matrix to be decomposed.

    It does so by:
        1.- Using the ldl function from the scipy.linalg module to perform the LDL
            decomposition of P.
        2.- Storing the lower triangular matrix of the decomposition in S.

    Returns:
        - S (numpy.ndarray): The lower triangular matrix of the decomposition.
    """
    L, D, perm = ldl(P)
    S = L @ sqrtm(D)
    return S

def givens_rotation(F, Q, S):
    """
    This function performs a Givens rotation on the matrix U to zero out the
    elements below the diagonal and ultimately output the upper triangular matrix.

    Parameters:
      - F (numpy.ndarray): The state transition matrix.
      - Q (numpy.ndarray): The process noise covariance matrix.
      - S (numpy.ndarray): The measurement noise covariance matrix.

    It does so by:
      1.- Concatenating the product of F.T and S.T with Q.T.
      2.- Looping through the matrix to perform the Givens rotation.
      3.- Storing the upper triangular matrix of the decomposition in S.

    Returns:
      - S (numpy.ndarray): The upper triangular matrix of the decomposition.
    """
    m = S.shape[0]
    U = np.block([[S.T @ F.T], [sqrtm(Q).T]])

    for j in range(m):
        for i in range(j + 1, 2 * m):
            B = np.eye(2 * m)
            a = U[j, j]
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

            B[i - 1, i - 1] = c
            B[i - 1, i] = s
            B[i, i - 1] = -s
            B[i, i] = c

            U = B.T @ U

    S = U[:m, :m].T
    return S

def potter_sqrt(x_t_p, S_t_p, y_t, H, R_sqrt):
    """
    Performs a square-root implementation of the Potter algorithm for updating 
    the state and covariance in a Kalman filter.

    Parameters:
        - x_t_p (numpy.ndarray): The predicted state vector at time t.
        - S_t_p (numpy.ndarray): The square root of the predicted state 
          covariance matrix at time t.
        - y_t (numpy.ndarray): The observation vector at time t.
        - H (numpy.ndarray): The observation matrix.
        - R_sqrt (numpy.ndarray): The square root of the observation noise 
          covariance matrix.

    Id does so by:
        1.- Computes the innovation vector `y` as the difference between the 
            observation and the predicted observation.
        2.- Computes the square root of the innovation covariance matrix `S` 
            using Cholesky decomposition.
        3.- Calculates the square-root form of the Kalman gain `K_sqrt`.
        4.- Updates the state vector `updated_x` using the innovation vector and
            `K_sqrt`.
        5.- Updates the square root of the state covariance matrix `updated_S` 
            using the Kalman gain and the observation matrix.

    Returns:
        - updated_x (numpy.ndarray): The updated state vector after 
          incorporating the observation.
        - updated_S (numpy.ndarray): The updated square root of the state 
          covariance matrix.
    """
    y = y_t - H @ x_t_p

    S = cholesky(R_sqrt.T @ R_sqrt + H @ S_t_p @ S_t_p.T @ H.T)

    K_sqrt = solve(S.T, (S_t_p.T @ H.T).T).T
    updated_x = x_t_p + K_sqrt @ solve(S.T, y)

    I_KH = np.eye(S_t_p.shape[0]) - K_sqrt @ H
    updated_S = I_KH @ S_t_p

    return updated_x, updated_S

def kalmanEnsemble(X, H):
    """
    This function performs the Ensemble Kalman filter on a given dataset X using 
    the observation matrix H.

    Parameters:
        - X (numpy.ndarray): The dataset to be filtered.
        - H (numpy.ndarray): The observation matrix.

    It does so by:
        1.- Getting the length of X and H.
        2.- Creating a list to store the filtered results.
        3.- Initializing the previous state and covariance matrix and applying 
        the square root filter on the covariance matrix.
        4.- Looping through the dataset calculating:
            - The transition matrix.
            - The process noise covariance matrix.
            - The measurement noise covariance matrix.
            - The predicted state and covariance matrix.

            To update the previous state and covariance matrix each step of 
            the loop, storing the states in the results list.

    Returns:
        - results (numpy.ndarray): A list of the predicted states.
    """
    len_x = X.shape[1]
    len_h = H.shape[0]
    results = []
    x_prev = np.zeros((len_x, 1))

    x_prev = X[0]
    P = np.cov(X.T)

    S = ldl_decomposition(P).T

    for i in range(1, len(X)):
        F = taylor_series(len_x) # Calculate the transition matrix

        w = np.random.normal(size=(len_x)) # Get the gaussian white noise of the process
        Q = np.eye(len_x) * np.std(w) # Calculate the process noise covariance matrix

        xp = F @ x_prev + w # Predict the next measurement
        Sp = givens_rotation(F, Q, S) # Predict the next S

        z = np.random.normal(size=(len_h)) # Get the gaussian white noise of the measurement
        R = np.eye(len_h) * np.std(z) # Calculate the measurement noise covariance matrix

        y_t = H @ X[i] + z

        x_prev, S = potter_sqrt(xp, Sp, y_t, H, R)

        results.append(x_prev)
    return np.array(results)

H_all, H_significant, H_non_significant = observation_matrices(m, m_significant, m_non_significant)
results_all = kalmanEnsemble(X, H_all)

def plot_signal(predicted_signal, original_signal, sensors, selected):
    """
    This function plots the predicted and original signals for a given set of
    sensors.

    Parameters:
      - predicted_signal (numpy.ndarray): The predicted signal.
      - original_signal (numpy.ndarray): The original signal.
      - sensors (list): The list of sensors.
      - selected (list): The list of selected sensors.

    It does so by:
      1.- Creating Pandas DataFrames from the predicted and original signals.
      2.- Plotting the predicted and original signals for the selected sensors.
    """
    prediction = pd.DataFrame(predicted_signal, columns=sensors)
    original = pd.DataFrame(original_signal, columns=sensors)

    plt.figure(figsize=(10, 6))
    plt.plot(prediction[selected], label='Predicted', color='red')
    plt.plot(original[selected], label='Original', color='blue')
    plt.xlabel('Time')
    plt.ylabel('Sensor Reading')
    plt.title(f'Sensors {selected}')
    plt.legend()
    plt.show()

plot_signal(results_all, X, sensors, sensors)