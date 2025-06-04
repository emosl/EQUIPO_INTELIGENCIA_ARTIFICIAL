# Kalman_Givens_Carlson.py
import numpy as np
import math
from scipy import linalg as lin
import time

# --- Helper functions ---

def observation_matrices(m_all, m_sig, m_nsig):
    H_all = np.eye(m_all)
    H_sig = np.zeros((m_sig, m_all))
    H_nsig = np.zeros((m_nsig, m_all))
    # last three sensors are "significant"
    H_sig[0, -3] = 1
    H_sig[1, -2] = 1
    H_sig[2, -1] = 1
    # the rest are non-significant
    for i in range(m_nsig):
        H_nsig[i, i] = 1
    return H_all, H_sig, H_nsig


def readSignal(path, samplingRate):
    data = np.genfromtxt(path, delimiter=',')
    data = np.delete(data, 0, axis=0)
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    return np.transpose(sessions, (0, 2, 1))


def taylor_series(Fs, m):
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def givens_rotation(F, Q, S):
    m = S.shape[0]
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    for j in range(U.shape[1]):
        for i in range(U.shape[0] - 1, j, -1):
            a, b = U[i-1, j], U[i, j]
            if b == 0:
                c, s = 1.0, 0.0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s = 1.0 / math.sqrt(1 + r*r)
                    c = s * r
                else:
                    r = b / a
                    c = 1.0 / math.sqrt(1 + r*r)
                    s = c * r
            G = np.eye(U.shape[0])
            G[i-1, i-1], G[i-1, i], G[i, i-1], G[i, i] = c, s, -s, c
            U = G.T @ U
    return U[:m, :m]


def noiseDiagCov(noise):
    n = noise.shape[0]
    D = np.zeros((n, n))
    variances = [np.cov(noise[i]) for i in range(n)]
    np.fill_diagonal(D, variances)
    return D


def getNextSquareRoot(P, Q, F, kind):
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return givens_rotation(F, Q, L).T
    else:
        return givens_rotation(F, Q, P).T


def carlsonFilter(S_prev, H, R, x_prev, y):
    n = x_prev.shape[0]
    m = y.shape[0]
    # ensure lower-triangular
    S = S_prev.copy()
    x = x_prev.copy()
    for j in range(m):
        H_j = H[j:j+1, :]
        phi = (S @ H_j.T).reshape(n, 1)
        d_prev = np.var(R[j])
        e_prev = np.zeros((n, 1))
        S_temp = np.zeros((n, n))
        for i in range(n):
            d_next = d_prev + float(phi[i]**2)
            b = math.sqrt(d_prev / d_next)
            c = float(phi[i] / math.sqrt(d_prev * d_next))
            e_next = e_prev + (S[:, i].reshape(n,1) * phi[i])
            col = (S[:, i].reshape(n,1) * b) - (e_prev * c)
            S_temp[:, i] = col.flatten()
            d_prev = d_next
            e_prev = e_next
        residual = float(y[j,0] - (H_j @ x)[0,0])
        x = x + e_prev * (residual / d_prev)
        S = S_temp
    return S, x


# --- Ensemble Kalman routine ---

def ensamble_kalman(nameSignal, Fs, wC):
    numberSensors = len(wC)
    invertWC = np.where(wC==1, 0, 1)
    signal = readSignal(nameSignal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(numberSensors, 3, numberSensors-3)

    n_sessions = len(signal)
    resultAll      = np.zeros((n_sessions, Fs))
    resultOriginal = np.zeros((n_sessions, Fs))
    resultWC       = np.zeros((n_sessions, Fs))
    resultNWC      = np.zeros((n_sessions, Fs))
    yAll, yWC, yNWC = [], [], []

    initialP = np.cov(signal[0])
    pk_all = initialP.copy()
    pk_sig = initialP.copy()
    pk_nsig = initialP.copy()
    x_all = np.zeros((numberSensors,1))
    x_sig = np.zeros((numberSensors,1))
    x_nsig = np.zeros((numberSensors,1))
    kind = 'initial'

    for i, block in enumerate(signal):
        for j in range(Fs):
            # Time update
            F = taylor_series(Fs, numberSensors)
            F_sig  = F.copy();  np.fill_diagonal(F_sig, wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)
            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i,j] = float(xpt_all.mean())
            resultWC[i,j]  = float(xpt_sig.mean())
            resultNWC[i,j] = float(xpt_nsig.mean())

            # Next measurement
            if j < Fs-1:
                nextState = block[:, j+1:j+2]
            else:
                next_block = signal[i+1] if i < n_sessions-1 else signal[0]
                nextState = next_block[:, 0:1]
            resultOriginal[i,j] = float(nextState.mean())
            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            # Noise covariances
            R_all  = noiseDiagCov(np.random.randn(numberSensors, numberSensors))
            R_sig  = noiseDiagCov(np.random.randn(3,3))
            R_nsig = noiseDiagCov(np.random.randn(numberSensors-3, numberSensors-3))

            # Square-root updates
            S_all  = getNextSquareRoot(pk_all,  np.eye(numberSensors), F, kind)
            S_sig  = getNextSquareRoot(pk_sig,  np.eye(numberSensors), F_sig, kind)
            S_nsig = getNextSquareRoot(pk_nsig, np.eye(numberSensors), F_nsig, kind)

            # Measurement updates via Carlson
            S_all,  x_all   = carlsonFilter(S_all,  H_all,  R_all,  xpt_all,  nextState)
            S_sig,  x_sig   = carlsonFilter(S_sig,  H_sig,  R_sig,  xpt_sig,  H_sig@nextState)
            S_nsig, x_nsig  = carlsonFilter(S_nsig, H_nsig, R_nsig, xpt_nsig, H_nsig@nextState)

            # Reconstruct covariances
            pk_all  = S_all @ S_all.T
            pk_sig  = S_sig @ S_sig.T
            pk_nsig = S_nsig @ S_nsig.T

            kind = 'other'

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC


def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)


if __name__ == '__main__':
    path = '/Users/emiliasalazar/.../KALMAN/S1.csv'
    Fs = 128
    w  = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    allRes, origRes, wcRes, nwcRes, yAll, yWC, yNWC = run(path, Fs, w)
    print(f"Execution time: {time.time() - start:.2f} seconds")