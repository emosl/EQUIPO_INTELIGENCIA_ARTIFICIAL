# Kalman_Householder_Potter.py
import numpy as np
import math
import time
from scipy import linalg as lin

# --- Helper functions ---

def observation_matrices(m_all, m_significant, m_non_significant):
    H_all = np.eye(m_all)
    H_significant = np.zeros((m_significant, m_all))
    H_non_significant = np.zeros((m_non_significant, m_all))
    # last three sensors are "significant"
    H_significant[0, -3] = 1
    H_significant[1, -2] = 1
    H_significant[2, -1] = 1
    # the rest are non-significant
    for i in range(m_non_significant):
        H_non_significant[i, i] = 1
    return H_all, H_significant, H_non_significant


def concatenateAmplitude(listSignal):
    return np.concatenate(listSignal, axis=None) if listSignal else np.zeros(0)


def readSignal(path, samplingRate):
    """
    Reads CSV, drops first column & header row, splits into sessions.
    Returns array of shape [n_sessions, n_sensors, n_samples].
    """
    data = np.genfromtxt(path, delimiter=',')[:, 1:]
    data = np.delete(data, 0, axis=0)
    sessions = []
    for i in range(0, len(data)//samplingRate * samplingRate, samplingRate):
        sessions.append(data[i : i + samplingRate])
    return np.transpose(sessions, (0, 2, 1))


def taylor_series(Fs, m):
    """Build the m×m Taylor‑series state‑transition matrix."""
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def householder_rotation(F, Q, S):
    """Compute square‑root time‑update via Householder QR decomposition."""
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    # QR decomposition (uses Householder reflections internally)
    _, R = np.linalg.qr(U, mode='reduced')
    m = S.shape[0]
    return R[:m, :m]


def Potter(S_p, H, R, x_p, y):
    """Potter covariance update."""
    x, S = x_p, S_p
    I = np.eye(len(x))
    for i in range(H.shape[0]):
        H_i = H[i:i+1]
        y_i = y[i]
        R_i = np.var(R[i])
        Phi = S.T @ H_i.T
        a = 1.0 / (Phi.T @ Phi + R_i)
        gamma = a / (1.0 + math.sqrt(a * R_i))
        S = S @ (I - (Phi @ Phi.T) * (a * gamma))
        K = S @ Phi
        x = x + K * (a * (y_i - H_i @ x))
    return S, x


def noiseDiagCov(noise):
    """Build a diagonal covariance matrix from noise samples."""
    n = noise.shape[0]
    D = np.zeros((n, n))
    variances = [np.cov(noise[i]) for i in range(n)]
    np.fill_diagonal(D, variances)
    return D


def getNextSquareRoot(P, Q, F, kind, method='householder'):
    """
    Compute next square‑root of covariance using Householder.
    kind: 'initial' or 'other'
    """
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return householder_rotation(F, Q, L).T
    else:
        return householder_rotation(F, Q, P).T

# --- Main filter routine ---

def run(nameSignal, Fs, wC):
    """
    Ensemble Kalman filter using Householder time update + Potter measurement update.
    nameSignal: path to EEG CSV
    Fs: sampling rate (e.g. 128)
    wC: binary mask for significant sensors (length = n_sensors)
    Returns: array [n_sessions, Fs] of filtered means.
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
            S = getNextSquareRoot(P, np.eye(m), F, kind, method='householder')

            # measurement update
            noise = noiseDiagCov(np.random.randn(m, m))
            S, x = Potter(S, H_all, noise, x_pred, session[:, j:j+1])
            P = S @ S.T

            out.append(x_pred.mean())
            kind = 'other'
        results.append(out)

    return np.array(results)

# --- Standalone execution ---

if __name__ == '__main__':
    path = '/Users/emiliasalazar/INTELIGENCIA_ARTIFICIAL/EQUIPO_INTELIGENCIA_ARTIFICIAL/KALMAN/S1.csv'
    Fs = 128
    w = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    filtered = run(path, Fs, w)
    print(f"Execution time: {time.time() - start:.2f} seconds")
