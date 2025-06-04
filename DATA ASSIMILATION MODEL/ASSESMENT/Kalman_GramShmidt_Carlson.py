# -*- coding: utf-8 -*-
"""
Kalman filter combining Carlson sequential measurement update (teacher's UD-style)
with Gram–Schmidt square-root time update, extended to return all 7 outputs.
"""
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
    return np.transpose(sessions, (0, 2, 1))  # [n_sess, sensors, samples]


def taylor_series(Fs, m):
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T


def gram_schmidt_rotation(F, Q, S):
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


def getNextSquareRoot(P, Q, F, kind):
    if kind == 'initial':
        Pm = (P + P.T) / 2
        lu, d, _ = lin.ldl(Pm, lower=True)
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        return gram_schmidt_rotation(F, Q, L).T
    else:
        return gram_schmidt_rotation(F, Q, P).T


def carlsonFilter(prevS, H, R, x_prev, y):
    n = x_prev.shape[0]
    m = y.shape[0]
    S_prev = prevS if np.allclose(prevS, np.tril(prevS)) else prevS.T
    x_new = x_prev.copy()
    for j in range(m):
        H_j = H[j:j+1, :]
        phi = (S_prev @ H_j.T).reshape(n, 1)
        d_prev = np.var(R[j])
        e_prev = np.zeros((n, 1))
        S_temp = np.zeros((n, n))
        for i in range(n):
            d_next = d_prev + float(phi[i]**2)
            b = math.sqrt(d_prev / d_next)
            c = float(phi[i] / math.sqrt(d_prev * d_next))
            e_next = e_prev + (S_prev[:, i].reshape(n,1) * phi[i])
            col = (S_prev[:, i].reshape(n,1) * b) - (e_prev * c)
            S_temp[:, i] = col.flatten()
            d_prev = d_next
            e_prev = e_next
        residual = (y[j,0] - (H_j @ x_new)[0,0])
        x_new = x_new + e_prev * (residual / d_prev)
        S_prev = S_temp
    return S_prev, x_new

# --- Extended EnKF to return 7 outputs ---

def ensamble_kalman(nameSignal, Fs, wC):
    m = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
    sig = readSignal(nameSignal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(m, 3, m-3)

    n_sess = len(sig)
    resultAll      = np.zeros((n_sess, Fs))
    resultOriginal = np.zeros((n_sess, Fs))
    resultWC       = np.zeros((n_sess, Fs))
    resultNWC      = np.zeros((n_sess, Fs))
    yAll, yWC, yNWC = [], [], []

    P_all = P_sig = P_nsig = np.cov(sig[0])
    x_all = x_sig = x_nsig = np.zeros((m,1))
    kind = 'initial'

    for i, block in enumerate(sig):
        for j in range(Fs):
            F      = taylor_series(Fs, m)
            F_sig  = F.copy();  np.fill_diagonal(F_sig, wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)

            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i,j] = float(xpt_all.mean())
            resultWC[i,j]  = float(xpt_sig.mean())
            resultNWC[i,j] = float(xpt_nsig.mean())

            if j < Fs-1:
                nextState = block[:, j+1:j+2]
            else:
                next_blk = sig[i+1] if i < n_sess-1 else sig[0]
                nextState = next_blk[:, 0:1]

            resultOriginal[i,j] = float(nextState.mean())
            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            R_all  = noiseDiagCov(np.random.randn(m, m))
            R_sig  = noiseDiagCov(np.random.randn(3,3))
            R_nsig = noiseDiagCov(np.random.randn(m-3,m-3))

            S_all  = getNextSquareRoot(P_all,  np.eye(m), F,     kind)
            S_sig  = getNextSquareRoot(P_sig,  np.eye(m), F_sig, kind)
            S_nsig = getNextSquareRoot(P_nsig, np.eye(m), F_nsig,kind)

            S_all,  x_all   = carlsonFilter(S_all,  H_all,  R_all,  xpt_all,  nextState)
            S_sig,  x_sig   = carlsonFilter(S_sig,  H_sig,  R_sig,  xpt_sig,  H_sig@nextState)
            S_nsig, x_nsig  = carlsonFilter(S_nsig, H_nsig, R_nsig, xpt_nsig, H_nsig@nextState)

            P_all  = S_all  @ S_all.T
            P_sig  = S_sig  @ S_sig.T
            P_nsig = S_nsig @ S_nsig.T

            kind = 'other'

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

# --- Adapter for batch script ---

def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)


if __name__ == '__main__':
    path = '/Users/emiliasalazar/.../KALMAN/S1.csv'
    Fs   = 128
    wC   = np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start = time.time()
    output = run(path, Fs, wC)
    print(f"Outputs shapes: {[o.shape if hasattr(o, 'shape') else len(o) for o in output]}")