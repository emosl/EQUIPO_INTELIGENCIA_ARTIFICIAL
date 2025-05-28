# Kalman_Potter_Givens.py
import numpy as np
import math
import time
from scipy import linalg as lin

# --- Helper functions ---

def observation_matrices(m_all, m_significant, m_non_significant):
    H_all            = np.eye(m_all)
    H_significant    = np.zeros((m_significant, m_all))
    H_non_significant= np.zeros((m_non_significant, m_all))
    # last three sensors are "significant"
    H_significant[0, -3] = 1
    H_significant[1, -2] = 1
    H_significant[2, -1] = 1
    # the rest are non-significant
    for i in range(m_non_significant):
        H_non_significant[i, i] = 1
    return H_all, H_significant, H_non_significant

def readSignal(path, samplingRate):
    data = np.genfromtxt(path, delimiter=',')
    data = np.delete(data, 0, axis=0)
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    # shape → [n_sessions, n_sensors, n_samples]
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
        for i in range(U.shape[0]-1, j, -1):
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

def getNextSquareRoot(P, Q, F, kind, method='givens'):
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return givens_rotation(F, Q, L).T
    else:
        return givens_rotation(F, Q, P).T

def Potter(S_p, H, R, x_p, y):
    x, S = x_p.copy(), S_p.copy()
    I = np.eye(len(x))
    for i in range(H.shape[0]):
        H_i = H[i:i+1]
        y_i = y[i, 0]
        R_i = np.var(R[i])
        Phi = S.T @ H_i.T
        a = 1.0 / (Phi.T @ Phi + R_i)
        gamma = a / (1 + math.sqrt(a * R_i))
        S = S @ (I - (Phi @ Phi.T) * (a * gamma))
        K = S @ Phi
        x = x + K * (a * (y_i - (H_i @ x)[0,0]))
    return S, x

# --- Ensemble Kalman wrapper returning all 7 outputs ---

def ensamble_kalman(nameSignal, Fs, wC):
    m = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
    sig = readSignal(nameSignal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(m, 3, m-3)

    # allocate outputs
    resultAll      = np.zeros((len(sig), Fs))
    resultOriginal = np.zeros((len(sig), Fs))
    resultWC       = np.zeros((len(sig), Fs))
    resultNWC      = np.zeros((len(sig), Fs))
    yAll, yWC, yNWC = [], [], []

    # initial state/covariance
    P_all = P_sig = P_nsig = np.cov(sig[0])
    x_all = x_sig = x_nsig = np.zeros((m,1))
    kind = 'initial'

    for i, block in enumerate(sig):
        for j in range(Fs):
            # time update
            F = taylor_series(Fs, m)
            F_sig  = F.copy();  np.fill_diagonal(F_sig,  wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)
            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i,j] = float(xpt_all.mean())
            resultWC[i,j]  = float(xpt_sig.mean())
            resultNWC[i,j] = float(xpt_nsig.mean())

            # measurement
            if j < Fs-1:
                nextState = block[:, j+1:j+2]
            else:
                next_block = sig[i+1] if i < len(sig)-1 else sig[0]
                nextState = next_block[:, 0:1]
            resultOriginal[i,j] = float(nextState.mean())
            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            # noise covariances
            R_all  = noiseDiagCov(np.random.randn(m, m))
            R_sig  = noiseDiagCov(np.random.randn(3,3))
            R_nsig = noiseDiagCov(np.random.randn(m-3, m-3))

            # square-root updates
            S_all  = getNextSquareRoot(P_all,  np.eye(m), F,     kind)
            S_sig  = getNextSquareRoot(P_sig,  np.eye(m), F_sig, kind)
            S_nsig = getNextSquareRoot(P_nsig, np.eye(m), F_nsig,kind)

            # measurement updates
            S_all,  x_all   = Potter(S_all,  H_all,  R_all,  xpt_all,  nextState)
            S_sig,  x_sig   = Potter(S_sig,  H_sig,  R_sig,  xpt_sig,  H_sig@nextState)
            S_nsig, x_nsig  = Potter(S_nsig, H_nsig, R_nsig, xpt_nsig, H_nsig@nextState)

            # reconstruct covariance
            P_all  = S_all @ S_all.T
            P_sig  = S_sig @ S_sig.T
            P_nsig = S_nsig @ S_nsig.T

            kind = 'other'

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)


if __name__ == '__main__':
    import time
    path = '/Users/.../KALMAN/S1.csv'
    Fs = 128
    w  = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    allRes, origRes, wcRes, nwcRes, yAll, yWC, yNWC = run(path, Fs, w)
    print(f"Execution time: {time.time() - start:.2f} seconds")
