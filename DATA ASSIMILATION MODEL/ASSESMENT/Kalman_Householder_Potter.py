import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as lin
import pandas as pd
import math
import os


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


def concatenateAmplitude(listSignal):
    """
    This function concatenates a list of signal arrays into a single array.

    Parameters:
        - listSignal (list): A list of numpy arrays representing signals.

    It does so by:
        1.- Checking if the input list is empty and returning a zero array if true.
        2.- Using numpy's concatenate function to merge all arrays in the list
            into a single array.

    Returns:
        - temp (numpy.ndarray): A concatenated array of all signals in the list.
    """
    if len(listSignal) == 0:
        return np.zeros([len(listSignal)])
    temp = listSignal[0]
    for i in range(1, len(listSignal)):
        temp = np.concatenate((temp, listSignal[i]), axis=None)
    return temp


def readSignal(nameSignal, samplingRate):
    """
    This function reads an EEG signal file and splits it into session matrices 
    based on the given sampling rate.

    Parameters:
        - nameSignal (str): The file path of the signal data.
        - samplingRate (int): The number of samples per second.

    It does so by:
        1.- Reading the signal file, excluding the first column.
        2.- Splitting the data into smaller matrices based on the sampling rate.
        3.- Transposing the resulting session matrices.

    Returns:
        - sessionMatrix (numpy.ndarray): A 3D array where each session is a 2D array
          of EEG data with dimensions [sessions, sensors, samples].
    """
    my_data = np.genfromtxt(nameSignal, delimiter=",")
    x = np.delete(my_data, (0), axis=0)
    sessionMatrix = []

    i = 0
    j = samplingRate

    for s in range(math.floor(len(x) / samplingRate)):
        sessionMatrix.append(np.asarray(x[i:j]))
        i = i + samplingRate
        j = j + samplingRate

    return np.transpose(sessionMatrix, (0, 2, 1))


def taylor_series(samplingRate, numSensors):
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
    c = np.zeros([numSensors, numSensors])

    for i in range(numSensors):
        v = (1 / samplingRate**i) / math.factorial(i)
        a = np.empty(numSensors)
        a.fill(v)
        np.fill_diagonal(c[i:], a)

    return c.T


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
    U = np.concatenate((S.T @ F.T, np.sqrt(Q).T), axis=0)

    for j in range(U.shape[1]):
        for i in range(U.shape[0] - 1, j, -1):
            B = np.eye(U.shape[0])

            a = U[i - 1, j]
            b = U[i, j]

            if b == 0:
                c = 1
                s = 0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s = 1 / np.sqrt(1 + r**2)
                    c = s * r
                else:
                    r = b / a
                    c = 1 / np.sqrt(1 + r**2)
                    s = c * r

            B[i - 1, i - 1] = c
            B[i - 1, i] = s
            B[i, i - 1] = -s
            B[i, i] = c

            U = B.T @ U

    S = U[:m, :m]
    return S


def Potter(S_p_t, H, R, x_p_t, y_t):
    """
    This function implements the Potter algorithm to update the Kalman filter state 
    and covariance matrices. It calculates the updated state estimate and its 
    corresponding covariance matrix based on the current measurements.

    Parameters:
        - S_p_t (numpy.ndarray): The prior square root covariance matrix.
        - H (numpy.ndarray): The observation matrix.
        - R (numpy.ndarray): The measurement noise covariance matrix.
        - x_p_t (numpy.ndarray): The predicted state vector.
        - y_t (numpy.ndarray): The measurement vector.

    It does so by:
        1.- Iteratively updating the covariance matrix and state vector for each observation.
        2.- Calculating the innovation (difference between observation and prediction).
        3.- Using a weighting factor (gamma_i) for stability.
        4.- Updating the square root covariance matrix using the innovation.

    Returns:
        - S_t (numpy.ndarray): The updated square root covariance matrix.
        - x_t (numpy.ndarray): The updated state vector.
    """
    x_t = x_p_t
    S_t = S_p_t
    I = np.eye(len(x_t))
    lenX = len(x_t)
    lenH = len(H)
    
    for i in range(lenH):
        H_i = H if H.shape == (1, lenH) else H[i].reshape((1, lenX))
        y_i_t = y_t[i] if y_t.shape == (lenH, 1) else y_t
        R_i = np.var(R[i])
        Phi_i = np.dot(S_t.T, H_i.T)
        a = 1 / (np.dot(Phi_i.T, Phi_i) + R_i)
        gamma_i = a / (1 + np.sqrt(a * R_i))

        S_p = np.dot(S_t, (I - np.dot(np.dot(Phi_i, Phi_i.T) * (a * gamma_i), np.eye(lenX))))

        K_i_t = np.dot(S_t, Phi_i)
        x_t = x_t + np.dot(K_i_t, a * (y_i_t - np.dot(H_i, x_t)))

        S_t = S_p  

    return S_t, x_t


def noiseDiagCov(noise):
    """
    This function creates a diagonal covariance matrix for the given noise.

    Parameters:
        - noise (numpy.ndarray): A 2D array where each row represents noise samples.

    It does so by:
        1.- Initializing a square zero matrix of size equal to the number of noise samples.
        2.- Filling the diagonal with the covariance of each noise sample.

    Returns:
        - noiseC (numpy.ndarray): A diagonal covariance matrix of the noise.
    """
    noiseC = np.zeros([len(noise), len(noise)])
    np.fill_diagonal(noiseC, [np.cov(num) for num in noise])
    return noiseC


def getNextSquareRoot(P, Q, F, typeM):
    """
    This function calculates the next square root matrix for the given covariance
    matrix using LDL decomposition and Givens rotation.

    Parameters:
        - P (numpy.ndarray): The process covariance matrix.
        - Q (numpy.ndarray): The process noise covariance matrix.
        - F (numpy.ndarray): The state transition matrix.
        - typeM (str): Indicates whether the initial or subsequent calculations 
          are being performed ("initial" or "other").

    It does so by:
        1.- Ensuring P is symmetric for stability.
        2.- Decomposing P into L and D matrices using LDL decomposition.
        3.- Applying Givens rotation to compute the square root matrix.

    Returns:
        - SnewT.T (numpy.ndarray): The square root of the updated covariance matrix.
    """
    SnewT = 0
    newP = P.copy()
    # Always symmetrize
    newP = (newP + newP.T) / 2.0

    if typeM == 'initial':
        try:
            lu, d, perm = lin.ldl(newP, lower=True)
            # Force positivity on diagonal of d
            epsilon = 1e-12
            for k in range(d.shape[0]):
                if d[k, k] < epsilon:
                    d[k, k] = epsilon
            L = lu.dot(lin.fractional_matrix_power(d, 0.5))

            SnewT = givens_rotation(F, Q, L)
        except np.linalg.LinAlgError:
            SnewT = np.zeros_like(P)
            return SnewT
    else:
        try:
            # At this point, P is already a valid square‐root from previous step
            SnewT = givens_rotation(F, Q, P)
        except np.linalg.LinAlgError:
            SnewT = np.zeros_like(P)
            return SnewT

    return SnewT.T


def ensamble_kalman(name_Signal, samplingRate, wC):
    """
    This function implements the Ensemble Kalman Filter (EnKF) to process EEG signals
    and generate results for different sensor configurations: all sensors, original data,
    significant sensors (Winning Combination, WC), and non-significant sensors (Not Winning Combination, NWC).

    Parameters:
        - name_Signal (str): Path to the CSV file containing EEG signal data.
        - samplingRate (int): Number of samples per second (sampling frequency).
        - wC (numpy.ndarray): Binary array representing significant sensors (1 for significant, 0 otherwise).

    Returns:
        - resultAll (numpy.ndarray): Filtered results for all sensors.
        - resultOriginal (numpy.ndarray): Filtered results for the original signal.
        - resultWC (numpy.ndarray): Filtered results for significant sensors (WC).
        - resultNWC (numpy.ndarray): Filtered results for non-significant sensors (NWC).
        - yResult (list): Measurements for all sensors.
        - yResult_WC (list): Measurements for significant sensors (WC).
        - yResult_NWC (list): Measurements for non-significant sensors (NWC).
    """
    numberSensors = len(wC)
    invertWC = np.where(wC == 1, 0, 1)

    signal = readSignal(name_Signal, samplingRate)
    Fs = 128
    m = 14
    m_significant = 3
    m_non_significant = 11
    H_all, H_significant, H_non_significant = observation_matrices(m, m_significant, m_non_significant)

    resultAll = np.zeros([len(signal), samplingRate])
    resultOriginal = np.zeros([len(signal), samplingRate])
    resultWC = np.zeros([len(signal), samplingRate])
    resultNWC = np.zeros([len(signal), samplingRate])

    resultAll_Temp = np.zeros([1, samplingRate])
    resultOriginal_Temp = np.zeros([1, samplingRate])
    resultWC_Temp = np.zeros([1, samplingRate])
    resultNWC_Temp = np.zeros([1, samplingRate])

    H = H_all
    H_WC = H_significant
    H_NWC = H_non_significant

    Q = np.eye(numberSensors)
    wNoise = np.zeros((numberSensors, 1))

    counterN = 1
    lastN = samplingRate - 1

    F = taylor_series(samplingRate, numberSensors)
    F_WC = taylor_series(samplingRate, numberSensors)
    np.fill_diagonal(F_WC[0:], wC)

    F_NWC = taylor_series(samplingRate, numberSensors)
    np.fill_diagonal(F_NWC[0:], invertWC)

    matrixState = signal[0]

    initialP = np.cov(matrixState)
    pk = initialP.copy()
    pk_WC = initialP.copy()
    pk_NWC = initialP.copy()
    ty = 'initial'

    x_preAll = np.zeros([numberSensors, 1])
    x_preWC = np.zeros([numberSensors, 1])
    x_preNWC = np.zeros([numberSensors, 1])

    yResult = []
    yResult_WC = []
    yResult_NWC = []

    for i in range(len(signal)):
        matrixState = signal[i]

        for j in range(samplingRate):
            x = x_preAll
            xWC = x_preWC
            xNWC = x_preNWC

            zNoiseMatrix = np.random.normal(0, 1, size=(numberSensors, numberSensors))
            zNoiseMatrixWC = np.random.normal(0, 1, size=(3, 3))
            zNoiseMatrixNWC = np.random.normal(0, 1, size=(numberSensors - 3, numberSensors - 3))

            R = noiseDiagCov(zNoiseMatrix)
            R_WC = noiseDiagCov(zNoiseMatrixWC)
            R_NWC = noiseDiagCov(zNoiseMatrixNWC)

            xpt = np.dot(F, x) + wNoise
            xpt_WC = np.dot(F_WC, xWC) + wNoise
            xpt_NWC = np.dot(F_NWC, xNWC) + wNoise

            resultAll_Temp[0, j] = np.sum(xpt) / numberSensors
            resultWC_Temp[0, j] = np.sum(xpt_WC) / 3
            resultNWC_Temp[0, j] = np.sum(xpt_NWC) / (numberSensors - 3)

            S_t = getNextSquareRoot(pk, Q, F, ty)
            S_tWC = getNextSquareRoot(pk_WC, Q, F_WC, ty)
            S_tNWC = getNextSquareRoot(pk_NWC, Q, F_NWC, ty)

            if j != lastN:
                nextState = matrixState[:, [counterN]]
                counterN += 1

            if j == samplingRate - 1 and i != len(signal) - 1:
                tempM = signal[i + 1]
                nextState = tempM[:, [0]]

            if j == samplingRate - 1 and i == len(signal) - 1:
                tempM = signal[0]
                nextState = tempM[:, [0]]

            resultOriginal_Temp[0, j] = np.sum(nextState) / numberSensors

            y = nextState
            yWC = np.dot(H_WC, nextState)
            yNWC = np.dot(H_NWC, nextState)

            yResult.append(np.sum(nextState) / numberSensors)
            yResult_WC.append(np.sum(yWC) / 3)
            yResult_NWC.append(np.sum(yNWC) / (numberSensors - 3))

            pk, x_preAll = Potter(S_t, H, R, xpt, y)
            pk_WC, x_preWC = Potter(S_tWC, H_WC, R_WC, xpt_WC, yWC)
            pk_NWC, x_preNWC = Potter(S_tNWC, H_NWC, R_NWC, xpt_NWC, yNWC)
            ty = 'other'

        resultAll[i] = resultAll_Temp
        resultOriginal[i] = resultOriginal_Temp
        resultWC[i] = resultWC_Temp
        resultNWC[i] = resultNWC_Temp

        resultAll_Temp = np.zeros([1, samplingRate])
        resultOriginal_Temp = np.zeros([1, samplingRate])
        resultWC_Temp = np.zeros([1, samplingRate])
        resultNWC_Temp = np.zeros([1, samplingRate])
        counterN = 1
        print(i)

    return resultAll, resultOriginal, resultWC, resultNWC, yResult, yResult_WC, yResult_NWC


# --- Adapter for command‐line testing ---
def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)

