# Kalman_Householder_Bierman.py
import numpy as np
import math
from scipy import linalg as lin
import time
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
    data = np.genfromtxt(path, delimiter=',')
    data = np.delete(data, 0, axis=0)
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    return np.transpose(sessions, (0, 2, 1))  # [n_sessions, sensors, samples]


def taylor_series(Fs, m):
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def householder_rotation(F, Q, S):
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    _, R = np.linalg.qr(U, mode='reduced')
    m = S.shape[0]
    return R[:m, :m]


def noiseDiagCov(noise):
    n = noise.shape[0]
    D = np.zeros((n, n))
    variances = [np.cov(noise[i]) for i in range(n)]
    np.fill_diagonal(D, variances)
    return D


def getNextSquareRoot(P, Q, F, kind, method='householder'):
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return householder_rotation(F, Q, L).T
    else:
        return householder_rotation(F, Q, P).T


def bierman_update(S_p, H, R, x_p, y):
    P_p = S_p @ S_p.T
    n = P_p.shape[0]
    D = np.diag(P_p).copy()
    U = np.eye(n)
    for i in range(n):
        for j in range(i):
            U[i, j] = P_p[i, j] / D[j]
    for k in range(H.shape[0]):
        Hi = H[k:k+1]
        yi = y[k, 0]
        Ri = R[k, k]
        phi = Hi @ U
        c = D * phi.ravel()
        alpha = Ri + phi @ c
        gain = c / alpha
        x_p = x_p + gain.reshape(-1,1) * (yi - Hi @ x_p)
        D = D - gain * c
        for m_i in range(1, n):
            for j in range(m_i):
                U[m_i, j] -= gain[m_i] * phi[0, j]
    P_upd = U @ np.diag(D) @ U.T
    S_t = np.linalg.cholesky(P_upd)
    return S_t, x_p

# --- Extended Ensemble Kalman returning seven outputs ---

def ensamble_kalman(nameSignal, Fs, wC):
    m = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
    sig = readSignal(nameSignal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(m, 3, m-3)

    sessions = len(sig)
    resultAll      = np.zeros((sessions, Fs))
    resultOriginal = np.zeros((sessions, Fs))
    resultWC       = np.zeros((sessions, Fs))
    resultNWC      = np.zeros((sessions, Fs))
    yAll, yWC, yNWC = [], [], []

    P_all = P_sig = P_nsig = np.cov(sig[0])
    x_all = x_sig = x_nsig = np.zeros((m,1))
    kind = 'initial'

    for i, block in enumerate(sig):
        for j in range(Fs):
            # Time update
            F      = taylor_series(Fs, m)
            F_sig  = F.copy();  np.fill_diagonal(F_sig,  wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)

            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i,j] = float(xpt_all.mean())
            resultWC[i,j]  = float(xpt_sig.mean())
            resultNWC[i,j] = float(xpt_nsig.mean())

            # Measurement
            if j < Fs-1:
                nextState = block[:, j+1:j+2]
            else:
                nxt = sig[i+1] if i < sessions-1 else sig[0]
                nextState = nxt[:, 0:1]
            resultOriginal[i,j] = float(nextState.mean())
            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            # Noise covariances
            R_all  = noiseDiagCov(np.random.randn(m, m))
            R_sig  = noiseDiagCov(np.random.randn(3, 3))
            R_nsig = noiseDiagCov(np.random.randn(m-3, m-3))

            # Covariance update
            S_all  = getNextSquareRoot(P_all,  np.eye(m), F,     kind)
            S_sig  = getNextSquareRoot(P_sig,  np.eye(m), F_sig, kind)
            S_nsig = getNextSquareRoot(P_nsig, np.eye(m), F_nsig,kind)

            # Measurement update
            S_all,  x_all   = bierman_update(S_all,  H_all,  R_all,  xpt_all,  nextState)
            S_sig,  x_sig   = bierman_update(S_sig,  H_sig,  R_sig,  xpt_sig,  H_sig@nextState)
            S_nsig, x_nsig  = bierman_update(S_nsig, H_nsig, R_nsig, xpt_nsig, H_nsig@nextState)

            # Reconstruct P
            P_all  = S_all  @ S_all.T
            P_sig  = S_sig  @ S_sig.T
            P_nsig = S_nsig @ S_nsig.T

            kind = 'other'

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

# Adapter for batch script

def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)


if __name__ == '__main__':
    import time
    path = '/Users/emiliasalazar/.../KALMAN/S1.csv'
    Fs   = 128
    wC   = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    outputs = run(path, Fs, wC)
    print([o.shape if hasattr(o, 'shape') else len(o) for o in outputs])
