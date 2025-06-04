# Kalman_Givens_Bierman.py
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


def bierman_update(S_p, H, R, x_p, y):
    P_p = S_p @ S_p.T
    n = P_p.shape[0]
    D = np.diag(P_p).copy()
    U = np.eye(n)
    for i in range(n):
        for j in range(i):
            U[i, j] = P_p[i, j] / D[j]
    for i in range(H.shape[0]):
        Hi = H[i:i+1]
        yi = y[i, 0]
        Ri = R[i, i]
        phi = Hi @ U
        c = D * phi.ravel()
        alpha = Ri + phi @ c
        k = c / alpha
        x_p = x_p + k.reshape(-1,1) * (yi - Hi @ x_p)
        D = D - k * c
        for m in range(1, n):
            for j in range(m):
                U[m, j] = U[m, j] - k[m] * phi[0, j]
    P_updated = U @ np.diag(D) @ U.T
    S_t = np.linalg.cholesky(P_updated)
    return S_t, x_p


# --- Ensemble filter for all variants ---

def ensamble_kalman(name_Signal, Fs, wC):
    numberSensors = len(wC)
    invertWC = np.where(wC==1, 0, 1)
    signal = readSignal(name_Signal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(numberSensors, 3, numberSensors-3)
    # prepare outputs
    resultAll      = np.zeros((len(signal), Fs))
    resultOriginal = np.zeros((len(signal), Fs))
    resultWC       = np.zeros((len(signal), Fs))
    resultNWC      = np.zeros((len(signal), Fs))
    yAll, yWC, yNWC = [], [], []
    # initial state & cov
    initialP = np.cov(signal[0])
    pk_all = pk_sig = pk_nsig = initialP.copy()
    x_all = x_sig = x_nsig = np.zeros((numberSensors,1))
    kind = 'initial'
    # process each session block
    for i, block in enumerate(signal):
        for j in range(Fs):
            # time update
            F = taylor_series(Fs, numberSensors)
            F_sig  = F.copy();  np.fill_diagonal(F_sig,  wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)
            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig
            # store prior means
            resultAll[i,j]      = np.mean(xpt_all)
            resultWC[i,j]       = np.mean(xpt_sig)
            resultNWC[i,j]      = np.mean(xpt_nsig)
            # measurement
            # determine nextState vector
            if j < Fs-1:
                nextState = block[:, j+1:j+2]
            else:
                nextState = (signal[i+1] if i<len(signal)-1 else signal[0])[:,0:1]
            resultOriginal[i,j] = np.mean(nextState)
            yAll.append(np.mean(nextState))
            yWC.append(np.mean(H_sig @ nextState))
            yNWC.append(np.mean(H_nsig @ nextState))
            # build noise covariances
            R_all  = noiseDiagCov(np.random.randn(numberSensors, numberSensors))
            R_sig  = noiseDiagCov(np.random.randn(3,3))
            R_nsig = noiseDiagCov(np.random.randn(numberSensors-3, numberSensors-3))
            # covariance update via sqrt
            S_all  = getNextSquareRoot(pk_all,  np.eye(numberSensors), F, kind)
            S_sig  = getNextSquareRoot(pk_sig,  np.eye(numberSensors), F_sig, kind)
            S_nsig = getNextSquareRoot(pk_nsig,np.eye(numberSensors), F_nsig, kind)
            # measurement update
            S_all,  x_all   = bierman_update(S_all,  H_all,  R_all,  xpt_all,  nextState)
            S_sig,  x_sig   = bierman_update(S_sig,  H_sig,  R_sig,  xpt_sig,  H_sig@nextState)
            S_nsig, x_nsig  = bierman_update(S_nsig, H_nsig, R_nsig, xpt_nsig, H_nsig@nextState)
            # reconstruct covariances
            pk_all  = S_all  @ S_all.T
            pk_sig  = S_sig  @ S_sig.T
            pk_nsig = S_nsig @ S_nsig.T
            kind = 'other'
    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

# --- Adapter for batch script ---
def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)

if __name__ == '__main__':
    path = '/Users/emiliasalazar/.../KALMAN/S1.csv'
    Fs = 128
    w  = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    allRes, origRes, wcRes, nwcRes, yAll, yWC, yNWC = run(path, Fs, w)
    print(f"Execution time: {time.time()-start:.2f}s")
