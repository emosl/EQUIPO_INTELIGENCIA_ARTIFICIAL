# Kalman_Householder_Bierman.py
import numpy as np
import math
import time
from scipy import linalg as lin

# --- Helper functions ---

def observation_matrices(m_all, m_significant, m_non_significant):
    H_all = np.eye(m_all)
    H_sig = np.zeros((m_significant, m_all))
    H_nsig = np.zeros((m_non_significant, m_all))
    # last three sensors are "significant"
    H_sig[0, -3] = 1
    H_sig[1, -2] = 1
    H_sig[2, -1] = 1
    # the rest are non-significant
    for i in range(m_non_significant):
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


def bierman_update(S_p, H, R, x_p, y):
    """
    UD-based Bierman measurement update.
    S_p: prior sqrt covariance (n x n)
    H: measurement matrix (m x n)
    R: measurement noise covariance (m x m)
    x_p: prior state estimate (n x 1)
    y: measurement vector (m x 1)
    Returns updated sqrt covariance S_t and state x_t.
    """
    # Reconstruct prior covariance
    P_p = S_p @ S_p.T
    n = P_p.shape[0]
    # UD decomposition: P_p = U * D * U^T
    D = np.diag(P_p).copy()
    U = np.eye(n)
    for i in range(n):
        for j in range(i):
            U[i, j] = P_p[i, j] / D[j]
    # Sequential Bierman updates
    for i in range(H.shape[0]):
        Hi = H[i:i+1]
        yi = y[i, 0]
        Ri = R[i, i]
        phi = Hi @ U           # (1 x n)
        c = D * phi.ravel()    # (n,)
        alpha = Ri + phi @ c   # scalar
        k = c / alpha          # (n,)
        # State update
        x_p = x_p + k.reshape(-1,1) * (yi - Hi @ x_p)
        # Covariance update
        D = D - k * c
        for m in range(1, n):
            for j in range(m):
                U[m, j] -= k[m] * phi[0, j]
    # Reconstruct sqrt covariance
    P_updated = U @ np.diag(D) @ U.T
    S_t = np.linalg.cholesky(P_updated)
    return S_t, x_p

# --- Main filter routine ---

def run(nameSignal, Fs, wC):
    """
    Ensemble Kalman filter using Householder time update + Bierman measurement update.
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
            # Time update
            F = taylor_series(Fs, m)
            x_pred = F @ x
            S = getNextSquareRoot(P, np.eye(m), F, kind)

            # Measurement update via Bierman
            noise = noiseDiagCov(np.random.randn(m, m))
            S, x = bierman_update(S, H_all, noise, x_pred, session[:, j:j+1])
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
