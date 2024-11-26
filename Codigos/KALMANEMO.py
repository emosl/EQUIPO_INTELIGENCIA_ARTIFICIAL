import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as lin
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

def observation_matrices(m_all, m_significant, m_non_significant):
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
    if len(listSignal) == 0:
        return np.zeros([len(listSignal)])
    temp = listSignal[0]
    for i in range(1, len(listSignal)):
        temp = np.concatenate((temp, listSignal[i]), axis=None)
    return temp


def readSignal(nameSignal, samplingRate):
    my_data = np.genfromtxt(nameSignal, delimiter=',')[:, 1:]
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
    c = np.zeros([numSensors, numSensors])

    for i in range(numSensors):
        v = (1 / samplingRate**i) / math.factorial(i)
        a = np.empty(numSensors)
        a.fill(v)
        np.fill_diagonal(c[i:], a)

    return c.T


def givens_rotation(F, Q, S):
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
    noiseC = np.zeros([len(noise), len(noise)])
    np.fill_diagonal(noiseC, [np.cov(num) for num in noise])
    return noiseC


def getNextSquareRoot(P,Q,F, typeM):
    SnewT = 0
    newP = P
    if (typeM == 'initial'):
        if(np.allclose(P, P.T) == 'false'):
            newP = (P + P.T)/2

        try:
            lu, d, perm = lin.ldl(newP, lower = 1)
            L = lu.dot(lin.fractional_matrix_power(d,0.5))

            SnewT = givens_rotation(F, Q, L)

        except np.linalg.LinAlgError:
            SnewT = 0
            return SnewT
    else:
        try:
            SnewT = givens_rotation(F, Q, P)
        except np.linalg.LinAlgError:
            SnewT = 0
            return SnewT

    return SnewT.T


def ensamble_kalman(name_Signal, samplingRate, wC):
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

import numpy as np
import os

input_folder = 'KALMAN'
output_folder = 'PROCESSED_KALMAN'


samplingRate = 128
aW = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1])


os.makedirs(output_folder, exist_ok=True)
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv') and file_name.startswith('S'):
        file_path = os.path.join(input_folder, file_name)
        name = os.path.splitext(file_name)[0]

        print(f"Processing {file_name}...")

        allResults, originalResults, wcResults, nwcResults, yResult, yResult_WC, yResult_NWC = ensamble_kalman(file_path, samplingRate, aW)

        amplitudeAll = concatenateAmplitude(allResults)
        amplitudeOriginal = concatenateAmplitude(originalResults)
        amplitudeWC = concatenateAmplitude(wcResults)
        amplitudeNWC = concatenateAmplitude(nwcResults)

        amplitudeYAll = np.array(yResult)
        amplitudeYWC = np.array(yResult_WC)
        amplitudeYNWC = np.array(yResult_NWC)
        np.savetxt(os.path.join(output_folder, f'{name}_amplitude_All.csv'), amplitudeAll, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_amplitude_Original.csv'), amplitudeOriginal, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_amplitude_WC.csv'), amplitudeWC, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_amplitude_NWC.csv'), amplitudeNWC, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_y_All.csv'), amplitudeYAll, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_y_WC.csv'), amplitudeYWC, delimiter=",")
        np.savetxt(os.path.join(output_folder, f'{name}_y_NWC.csv'), amplitudeYNWC, delimiter=",")

        print(f"Processed and saved results for {file_name}")
