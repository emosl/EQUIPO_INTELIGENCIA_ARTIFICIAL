# Kalman_Householder_Carlson.py
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
    data = np.genfromtxt(path, delimiter=',')[:, 1:]
    data = np.delete(data, 0, axis=0)
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    return np.transpose(sessions, (0, 2, 1))


def taylor_series(Fs, m):
    """Build the m×m Taylor-series state-transition matrix."""
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def householder_rotation(F, Q, S):
    """Compute square-root time-update via Householder QR decomposition."""
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    # QR via Householder reflections internally
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


def getNextSquareRoot(P, Q, F, kind, method='householder'):
    """
    Compute next square-root of covariance using Householder.
    kind: 'initial' or 'other'
    """
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return householder_rotation(F, Q, L).T
    else:
        return householder_rotation(F, Q, P).T


def carlson_sqrt_update(S_p, H, R, x_p, y):
    """
    True Carlson square-root Kalman update using QR decomposition.
    S_p: sqrt of prior covariance (n x n)
    H: measurement matrix (m x n)
    R: measurement noise covariance (m x m)
    x_p: prior state estimate (n x 1)
    y: measurement vector (m x 1)
    Returns updated sqrt covariance S_t and state x_t.
    """
    # 1. Form stacked matrix for QR
    R_chol = np.linalg.cholesky(R)
    top = np.hstack([R_chol, np.zeros((R.shape[0], S_p.shape[1]))])
    bottom = np.hstack([H @ S_p, S_p])
    A = np.vstack([top, bottom])

    # 2. QR decomposition of A.T, then take R.T
    _, R_mat = np.linalg.qr(A.T)
    S_t = R_mat.T[S_p.shape[0]:, S_p.shape[1]:]

    # 3. Innovation and Kalman gain
    P_p = S_p @ S_p.T
    PHt = P_p @ H.T
    S_ht = H @ PHt + R
    K = PHt @ np.linalg.inv(S_ht)

    x_t = x_p + K @ (y - H @ x_p)
    return S_t, x_t

# --- Main filter routine ---

def run(nameSignal, Fs, wC):
    """
    Ensemble Kalman filter using Householder time update + Carlson measurement update.
    nameSignal: path to EEG CSV
    Fs: sampling rate (e.g. 128)
    wC: binary mask for significant sensors
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
            S = getNextSquareRoot(P, np.eye(m), F, kind)

            # measurement update
            noise = noiseDiagCov(np.random.randn(m, m))
            S, x = carlson_sqrt_update(S, H_all, noise, x_pred, session[:, j:j+1])
            P = S @ S.T

            out.append(x_pred.mean())
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
