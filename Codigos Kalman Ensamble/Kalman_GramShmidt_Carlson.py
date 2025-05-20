# -*- coding: utf-8 -*-
"""
Kalman filter combining Carlson sequential measurement update (teacher's UD-style) 
with Gram–Schmidt square-root time update.
"""
import numpy as np
import math
import time
from scipy import linalg as lin

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
    """
    Reads CSV, drops first column & header row, splits into sessions.
    Returns array of shape [n_sessions, n_sensors, n_samples].
    """
    data = np.genfromtxt(path, delimiter=',')
    data = np.delete(data, 0, axis=0)
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    return np.transpose(sessions, (0, 2, 1))


def taylor_series(Fs, m):
    """Builds the m×m Taylor-series state-transition matrix."""
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def gram_schmidt_rotation(F, Q, S):
    """Compute square-root time-update via QR decomposition."""
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    _, R = np.linalg.qr(U, mode='reduced')
    m = S.shape[0]
    return R[:m, :m]


def noiseDiagCov(noise):
    """Build a diagonal covariance matrix from noise samples."""
    n = noise.shape[0]
    D = np.zeros((n, n))
    variances = [np.cov(noise[i]) for i in range(n)]
    np.fill_diagonal(D, variances)
    return D


def getNextSquareRoot(P, Q, F, kind, method='gram_schmidt'):
    """
    Compute next square-root of covariance using Gram–Schmidt.
    kind: 'initial' or 'other'
    """
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return gram_schmidt_rotation(F, Q, L).T
    else:
        return gram_schmidt_rotation(F, Q, P).T


def carlsonFilter(prevS, H, R, x_prev, y):
    """
    Teacher's sequential Carlson UD-style measurement update.
    prevS: prior sqrt covariance (n×n, lower-triangular)
    H: measurement matrix (m×n)
    R: measurement noise samples (m×m)
    x_prev: prior state estimate (n×1)
    y: measurement vector (m×1)
    Returns (S_new, x_new).
    """
    n = x_prev.shape[0]
    m = y.shape[0]
    # Ensure S_prev is lower-triangular
    S_prev = prevS if np.allclose(prevS, np.tril(prevS)) else prevS.T
    x_new = x_prev.copy()

    # Sequential per-scalar update
    for j in range(m):
        # extract scalar measurement
        H_j = H[j:j+1, :]
        phi = (S_prev @ H_j.T).reshape(n, 1)
        d_prev = np.var(R[j])
        e_prev = np.zeros((n, 1))
        S_temp = np.zeros((n, n))

        # UD-recursion across state dims
        for i in range(n):
            d_next = d_prev + float(phi[i]**2)
            b = math.sqrt(d_prev / d_next)
            c = float(phi[i] / math.sqrt(d_prev * d_next))
            e_next = e_prev + (S_prev[:, i].reshape(n,1) * phi[i])
            col = (S_prev[:, i].reshape(n,1) * b) - (e_prev * c)
            S_temp[:, i] = col.flatten()
            d_prev = d_next
            e_prev = e_next

        # state update scalar
        residual = (y[j,0] - (H_j @ x_new)[0,0])
        x_new = x_new + e_prev * (residual / d_prev)
        S_prev = S_temp

    return S_prev, x_new

# --- Main filter routine ---

def run(nameSignal, Fs, wC):
    """
    Ensemble Kalman filter using Carlson sequential measurement + Gram–Schmidt time update.
    nameSignal: EEG CSV path
    Fs: sampling rate
    wC: binary mask for significant sensors
    Returns: array [n_sessions, Fs] of filtered means (posterior).
    """
    m = len(wC)
    sig = readSignal(nameSignal, Fs)
    H_all, _, _ = observation_matrices(m, 3, m - 3)

    x = np.zeros((m, 1))
    P = np.cov(sig[0])
    kind = 'initial'
    results = []

    for session in sig:
        out = []
        for j in range(Fs):
            # time update
            F = taylor_series(Fs, m)
            x_pred = F @ x
            S = getNextSquareRoot(P, np.eye(m), F, kind)

            # measurement update using teacher's Carlson
            noise = noiseDiagCov(np.random.randn(m, m))
            S, x = carlsonFilter(S, H_all, noise, x_pred, session[:, j:j+1])
            P = S @ S.T

            # store posterior mean
            out.append(float(x.mean()))
            kind = 'other'
        results.append(out)

    return np.array(results)

if __name__ == '__main__':
    path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN/S1.csv'
    Fs = 128
    w = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    filtered = run(path, Fs, w)
    print(f"Execution time: {time.time() - start:.2f} seconds")
