import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as lin
import pandas as pd
import math
import os
import time

def observation_matrices(m_all, m_significant, m_non_significant):
    """
    Creates observation matrices for all sensors, significant sensors, 
    and non-significant sensors.
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
    Concatenates a list of signal arrays into one 1D array.
    """
    if len(listSignal) == 0:
        return np.zeros([len(listSignal)])
    temp = listSignal[0]
    for i in range(1, len(listSignal)):
        temp = np.concatenate((temp, listSignal[i]), axis=None)
    return temp

def readSignal(nameSignal, samplingRate, sensor_count):
    """
    Reads an EEG signal CSV file and splits it into sessions based on the sampling rate.
    
    If the CSV file has one more column than sensor_count (for example, a counter or timestamp), 
    that first column is removed.
    
    Returns a 3D array of shape (sessions, sensors, samples).
    """
    # Skip the header row
    data = np.genfromtxt(nameSignal, delimiter=',', skip_header=1)
    # If the number of columns is sensor_count+1, assume the first column is extra and remove it.
    if data.shape[1] == sensor_count + 1:
        data = data[:, 1:]
    # Otherwise, if data.shape[1] equals sensor_count, we assume it is already correct.
    sessionMatrix = []
    i = 0
    j = samplingRate
    for s in range(math.floor(len(data) / samplingRate)):
        sessionMatrix.append(np.asarray(data[i:j]))
        i += samplingRate
        j += samplingRate
    return np.transpose(sessionMatrix, (0, 2, 1))

def taylor_series(samplingRate, numSensors):
    """
    Generates the Taylor series (state transition) matrix.
    
    For each row i, the diagonal of the submatrix c[i:] has length (numSensors - i).
    """
    c = np.zeros((numSensors, numSensors))
    for i in range(numSensors):
        v = (1 / samplingRate**i) / math.factorial(i)
        a = np.empty(numSensors - i)
        a.fill(v)
        np.fill_diagonal(c[i:], a)
    return c.T

def givens_rotation(F, Q, S):
    """
    Uses Givens rotations to compute an upper triangular matrix.
    
    The routine first computes U = [S.T @ F.T; np.sqrt(Q).T] and then applies
    successive rotations to zero out the sub-diagonal elements.
    """
    m = S.shape[0]
    U = np.concatenate((S.T @ F.T, np.sqrt(Q).T), axis=0)
    for j in range(U.shape[1]):
        for i in range(U.shape[0] - 1, j, -1):
            B = np.eye(U.shape[0])
            a = U[i - 1, j]
            b = U[i, j]
            if b == 0:
                c_val = 1
                s_val = 0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s_val = 1 / np.sqrt(1 + r**2)
                    c_val = s_val * r
                else:
                    r = b / a
                    c_val = 1 / np.sqrt(1 + r**2)
                    s_val = c_val * r
            B[i - 1, i - 1] = c_val
            B[i - 1, i] = s_val
            B[i, i - 1] = -s_val
            B[i, i] = c_val
            U = B.T @ U
    S_out = U[:m, :m]
    return S_out

def gram_schmidt_rotation(F, Q, S):
    """
    Uses Gram–Schmidt (via QR decomposition) to compute the upper triangular matrix.
    
    It forms U the same way as in the Givens routine and then uses np.linalg.qr.
    """
    m = S.shape[0]
    U = np.concatenate((S.T @ F.T, np.sqrt(Q).T), axis=0)
    Q_mat, R = np.linalg.qr(U, mode='reduced')
    return R[:m, :m]

def Potter(S_p_t, H, R, x_p_t, y_t):
    """
    Implements the Potter algorithm to update the state and covariance.
    
    Updates the state estimate x and square-root covariance matrix S_p_t based on
    the observation y_t.
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
    Builds a diagonal covariance matrix from the given noise samples.
    """
    noiseC = np.zeros([len(noise), len(noise)])
    np.fill_diagonal(noiseC, [np.cov(num) for num in noise])
    return noiseC

def getNextSquareRoot(P, Q, F, typeM, method='gram_schmidt'):
    """
    Computes the next square root matrix using either Givens rotations or Gram–Schmidt.
    
    Parameters:
      - P: Process covariance matrix.
      - Q: Process noise covariance matrix.
      - F: State transition matrix.
      - typeM: 'initial' or 'other'.
      - method: 'givens' or 'gram_schmidt'.
      
    Returns:
      - The transpose of the computed square root matrix.
    """
    SnewT = 0
    newP = P
    if typeM == 'initial':
        if not np.allclose(P, P.T):
            newP = (P + P.T) / 2
        try:
            lu, d, perm = lin.ldl(newP, lower=True)
            L = lu.dot(lin.fractional_matrix_power(d, 0.5))
            if method == 'givens':
                SnewT = givens_rotation(F, Q, L)
            elif method == 'gram_schmidt':
                SnewT = gram_schmidt_rotation(F, Q, L)
            else:
                raise ValueError("Unknown rotation method")
        except np.linalg.LinAlgError:
            SnewT = 0
            return SnewT
    else:
        try:
            if method == 'givens':
                SnewT = givens_rotation(F, Q, P)
            elif method == 'gram_schmidt':
                SnewT = gram_schmidt_rotation(F, Q, P)
            else:
                raise ValueError("Unknown rotation method")
        except np.linalg.LinAlgError:
            SnewT = 0
            return SnewT
    return SnewT.T

def ensamble_kalman(name_Signal, samplingRate, wC, rotation_method='gram_schmidt'):
    """
    Implements the Ensemble Kalman Filter on EEG data using the selected rotation method.
    
    Parameters:
      - name_Signal: Path to the EEG CSV file.
      - samplingRate: Sampling frequency.
      - wC: Binary array for significant sensors.
      - rotation_method: 'givens' or 'gram_schmidt'.
      
    Returns:
      - Filtered results and measurement arrays.
    """
    numberSensors = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
   
    signal = readSignal(name_Signal, samplingRate, sensor_count=numberSensors)

    Fs = 128  
    m = numberSensors  
    m_significant = 3 
    m_non_significant = numberSensors - 3  
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
    pk = initialP
    pk_WC = initialP
    pk_NWC = initialP
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
            zNoiseMatrixWC = np.random.normal(0, 1, size=(m_significant, m_significant))
            zNoiseMatrixNWC = np.random.normal(0, 1, size=(m_non_significant, m_non_significant))
            
            R = noiseDiagCov(zNoiseMatrix)
            R_WC = noiseDiagCov(zNoiseMatrixWC)
            R_NWC = noiseDiagCov(zNoiseMatrixNWC)
            
            xpt = np.dot(F, x) + wNoise
            xpt_WC = np.dot(F_WC, xWC) + wNoise
            xpt_NWC = np.dot(F_NWC, xNWC) + wNoise
            
            resultAll_Temp[0, j] = np.sum(xpt) / numberSensors
            resultWC_Temp[0, j] = np.sum(xpt_WC) / m_significant
            resultNWC_Temp[0, j] = np.sum(xpt_NWC) / m_non_significant

            S_t = getNextSquareRoot(pk, Q, F, ty, rotation_method)
            S_tWC = getNextSquareRoot(pk_WC, Q, F_WC, ty, rotation_method)
            S_tNWC = getNextSquareRoot(pk_NWC, Q, F_NWC, ty, rotation_method)
            
            if j != lastN:
                nextState = matrixState[:, [counterN]]
                counterN += 1
            elif j == samplingRate - 1 and i != len(signal) - 1:
                tempM = signal[i + 1]
                nextState = tempM[:, [0]]
            else: 
                tempM = signal[0]
                nextState = tempM[:, [0]]
            
            resultOriginal_Temp[0, j] = np.sum(nextState) / numberSensors
            
            y = nextState
            yWC = np.dot(H_WC, nextState)
            yNWC = np.dot(H_NWC, nextState)
            
            yResult.append(np.sum(nextState) / numberSensors)
            yResult_WC.append(np.sum(yWC) / m_significant)
            yResult_NWC.append(np.sum(yNWC) / m_non_significant)
            
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
        print("Processed session:", i)
    
    return resultAll, resultOriginal, resultWC, resultNWC, yResult, yResult_WC, yResult_NWC


file_path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/Grabaciones/KalmanTest.csv'  # Update with your file path
output_folder = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/PROCESSED_KALMAN'
samplingRate = 128
# For S17 the winning combination vector was length 14.
aW = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
os.makedirs(output_folder, exist_ok=True)

# Measure execution time with Givens rotation
start_time = time.time()
results_givens = ensamble_kalman(file_path, samplingRate, aW, rotation_method='givens')
end_time = time.time()
print("Execution time with Givens rotation:", end_time - start_time, "seconds")

# Measure execution time with Gram-Schmidt rotation
start_time = time.time()
results_gs = ensamble_kalman(file_path, samplingRate, aW, rotation_method='gram_schmidt')
end_time = time.time()
print("Execution time with Gram-Schmidt:", end_time - start_time, "seconds")


resultAll, resultOriginal, resultWC, resultNWC, yResult, yResult_WC, yResult_NWC = results_gs


amplitudeAll = concatenateAmplitude(resultAll)
amplitudeOriginal = concatenateAmplitude(resultOriginal)
amplitudeWC = concatenateAmplitude(resultWC)
amplitudeNWC = concatenateAmplitude(resultNWC)
amplitudeYAll = np.array(yResult)
amplitudeYWC = np.array(yResult_WC)
amplitudeYNWC = np.array(yResult_NWC)


name = 'STest' 
np.savetxt(os.path.join(output_folder, f'{name}_amplitude_All.csv'), amplitudeAll, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_amplitude_Original.csv'), amplitudeOriginal, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_amplitude_WC.csv'), amplitudeWC, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_amplitude_NWC.csv'), amplitudeNWC, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_y_All.csv'), amplitudeYAll, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_y_WC.csv'), amplitudeYWC, delimiter=",")
np.savetxt(os.path.join(output_folder, f'{name}_y_NWC.csv'), amplitudeYNWC, delimiter=",")

print(f"Processed and saved results for {name}")
