# Kalman_Givens_Bierman_fixed.py
import numpy as np
import math
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
    data = np.delete(data, 0, axis=0)  # drop header row
    sessions = []
    total = (len(data) // samplingRate) * samplingRate
    for i in range(0, total, samplingRate):
        sessions.append(data[i : i + samplingRate])
    # shape → [n_sessions, n_sensors, n_samples]
    return np.transpose(sessions, (0, 2, 1))

def taylor_series(Fs, m):
    """Build the m×m Taylor‐series state‐transition matrix."""
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T

def givens_rotation(F, Q, S):
    """
    Given prior S (square‐root cov), F, and Q,
    form U = [ Sᵀ·Fᵀ ; sqrt(Q)ᵀ ], perform Givens‐QR,
    and return the top m×m block of R.
    """
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    for j in range(U.shape[1]):
        for i in range(U.shape[0] - 1, j, -1):
            a, b = U[i - 1, j], U[i, j]
            if b == 0:
                c, s = 1.0, 0.0
            else:
                if abs(b) > abs(a):
                    r = a / b
                    s = 1.0 / math.sqrt(1 + r * r)
                    c = s * r
                else:
                    r = b / a
                    c = 1.0 / math.sqrt(1 + r * r)
                    s = c * r
            G = np.eye(U.shape[0])
            G[i - 1, i - 1], G[i - 1, i], G[i, i - 1], G[i, i] = c, s, -s, c
            U = G.T @ U
    m = S.shape[0]
    return U[:m, :m]

def noiseDiagCov(noise):
    """
    Build a diagonal covariance matrix from each row of `noise`.
    """
    n = noise.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        D[i, i] = np.var(noise[i])
    return D

def getNextSquareRoot(prev, Q, F, kind):
    """
    If kind == 'initial', prev is full covariance P:
      - Symmetrize P, perform LDL, form L·D^{1/2} with small‐eigenvalue clipping,
        then apply Givens‐QR to get square‐root.
    If kind == 'other', prev is already a square‐root S: apply Givens‐QR directly.
    Returns S_new so that new covariance = S_new·S_newᵀ.
    """
    epsilon = 1e-12
    if kind == 'initial':
        Pm = (prev + prev.T) / 2.0
        lu, d, _ = lin.ldl(Pm, lower=True)
        for k in range(d.shape[0]):
            if d[k, k] < epsilon:
                d[k, k] = epsilon
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        Snew = givens_rotation(F, Q, L)
        return Snew.T
    else:
        # prev is already square‐root S
        Snew = givens_rotation(F, Q, prev)
        return Snew.T

def bierman_update(S_p, H, R, x_p, y):
    """
    UD-based Bierman measurement update.
    Returns updated square‐root covariance S_t and state x_t.
    """
    epsilon = 1e-12
    P_p = S_p @ S_p.T
    n = P_p.shape[0]
    D = np.diag(P_p).copy()
    U = np.eye(n)
    # build U s.t. P_p = U·diag(D)·Uᵀ
    for i in range(n):
        for j in range(i):
            U[i, j] = P_p[i, j] / D[j]
    # sequential update
    for k in range(H.shape[0]):
        Hi = H[k : k + 1]      # (1×n)
        yi = y[k, 0]           # scalar
        Ri = R[k, k]           # scalar variance

        phi = Hi @ U           # (1×n)
        c = (D * phi.ravel()).reshape(n, 1)   # (n×1)
        alpha = Ri + (phi @ c)[0, 0]
        gain = c / alpha       # (n×1)

        # state update
        residual = yi - (Hi @ x_p)[0, 0]
        x_p = x_p + gain * residual

        # D update
        D = D - (gain.ravel() * c.ravel())

        # U update
        for mi in range(1, n):
            for j in range(mi):
                U[mi, j] -= gain[mi, 0] * phi[0, j]

        # ensure D ≥ ε
        for idx in range(n):
            if D[idx] < epsilon:
                D[idx] = epsilon

    P_upd = U @ np.diag(D) @ U.T
    S_t = np.linalg.cholesky((P_upd + P_upd.T) / 2.0)
    return S_t, x_p

# --- Ensemble Kalman wrapper returning all 7 outputs ---

def ensamble_kalman(name_Signal, Fs, wC):
    numberSensors = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
    signal = readSignal(name_Signal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(numberSensors, 3, numberSensors - 3)

    n_sessions = len(signal)
    resultAll      = np.zeros((n_sessions, Fs))
    resultOriginal = np.zeros((n_sessions, Fs))
    resultWC       = np.zeros((n_sessions, Fs))
    resultNWC      = np.zeros((n_sessions, Fs))
    yAll, yWC, yNWC = [], [], []

    # Initial full covariance & states
    initialP = np.cov(signal[0])
    pk_all   = initialP.copy()
    pk_sig   = initialP.copy()
    pk_nsig  = initialP.copy()
    x_all  = np.zeros((numberSensors, 1))
    x_sig  = np.zeros((numberSensors, 1))
    x_nsig = np.zeros((numberSensors, 1))
    kind = 'initial'

    # Precompute first F‐matrices and Q
    F0      = taylor_series(Fs, numberSensors)
    F0_sig  = F0.copy();   np.fill_diagonal(F0_sig,  wC)
    F0_nsig = F0.copy();   np.fill_diagonal(F0_nsig, invertWC)
    Q_eye   = np.eye(numberSensors)

    # Initial square‐roots
    S_all  = getNextSquareRoot(pk_all,  Q_eye, F0,      'initial')
    S_sig  = getNextSquareRoot(pk_sig,  Q_eye, F0_sig,  'initial')
    S_nsig = getNextSquareRoot(pk_nsig, Q_eye, F0_nsig, 'initial')

    for i, block in enumerate(signal):
        for j in range(Fs):
            # --- TIME UPDATE ---
            F = taylor_series(Fs, numberSensors)
            F_sig  = F.copy();   np.fill_diagonal(F_sig,  wC)
            F_nsig = F.copy();   np.fill_diagonal(F_nsig, invertWC)

            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i, j]  = float(xpt_all.mean())
            resultWC[i, j]   = float(xpt_sig.mean())
            resultNWC[i, j]  = float(xpt_nsig.mean())

            # --- MEASUREMENT nextState ---
            if j < Fs - 1:
                nextState = block[:, j + 1 : j + 2]
            else:
                if i < n_sessions - 1:
                    nextState = signal[i + 1][:, 0 : 1]
                else:
                    nextState = signal[0][:, 0 : 1]
            resultOriginal[i, j] = float(nextState.mean())

            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            # --- NOISE COVARIANCES ---
            R_all  = noiseDiagCov(np.random.randn(numberSensors, numberSensors))
            R_sig  = noiseDiagCov(np.random.randn(3, 3))
            R_nsig = noiseDiagCov(np.random.randn(numberSensors - 3, numberSensors - 3))

            # --- SQUARE‐ROOT TIME UPDATE (Givens) ---
            if kind == 'initial':
                S_all  = getNextSquareRoot(pk_all,  Q_eye, F,      'initial')
                S_sig  = getNextSquareRoot(pk_sig,  Q_eye, F_sig,  'initial')
                S_nsig = getNextSquareRoot(pk_nsig, Q_eye, F_nsig, 'initial')
            else:
                S_all  = getNextSquareRoot(S_all,  Q_eye, F,      'other')
                S_sig  = getNextSquareRoot(S_sig,  Q_eye, F_sig,  'other')
                S_nsig = getNextSquareRoot(S_nsig, Q_eye, F_nsig, 'other')

            # --- MEASUREMENT UPDATE (Bierman UD) ---
            S_all,  x_all   = bierman_update(S_all,  H_all,  R_all,   xpt_all,       nextState)
            S_sig,  x_sig   = bierman_update(S_sig,  H_sig,  R_sig,   xpt_sig,       H_sig @ nextState)
            S_nsig, x_nsig  = bierman_update(S_nsig, H_nsig, R_nsig,  xpt_nsig,      H_nsig @ nextState)

            # Reconstruct full covariance (for bookkeeping)
            pk_all  = S_all @ S_all.T
            pk_sig  = S_sig @ S_sig.T
            pk_nsig = S_nsig @ S_nsig.T

            kind = 'other'
        # end inner loop
    # end outer loop

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

# --- Adapter for batch script ---
def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)

if __name__ == '__main__':
    # Prevent auto‐execution on import
    pass
