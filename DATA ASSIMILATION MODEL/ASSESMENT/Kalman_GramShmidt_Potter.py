# Kalman_Potter_GramSchmidt_fixed.py
import numpy as np
import math
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


def noiseDiagCov(noise):
    n = noise.shape[0]
    D = np.zeros((n, n))
    variances = [np.cov(noise[i]) for i in range(n)]
    np.fill_diagonal(D, variances)
    return D


def gram_schmidt_rotation(F, Q, S):
    """
    Assemble [Sᵀ·Fᵀ; sqrt(Q)ᵀ], perform QR via NumPy (which uses Gram–Schmidt internally),
    then return the top m×m block of R.
    """
    U = np.vstack((S.T @ F.T, np.sqrt(Q).T))
    _, R = np.linalg.qr(U, mode='reduced')
    m = S.shape[0]
    return R[:m, :m]


def getNextSquareRoot(prev, Q, F, kind):
    """
    If kind == 'initial': prev is full covariance P.
       - Symmetrize, do LDL => L·D·Lᵀ, clamp D ≥ ε, form L·D^{½}, then apply Gram–Schmidt QR.
    If kind == 'other': prev is already square-root S. Apply Gram–Schmidt QR directly.
    Returns S_new so that new covariance = S_new·S_newᵀ.
    """
    epsilon = 1e-12
    if kind == 'initial':
        Pm = (prev + prev.T) / 2.0
        lu, d, _ = lin.ldl(Pm, lower=True)
        # Ensure D's diagonal ≥ ε
        for k in range(d.shape[0]):
            if d[k, k] < epsilon:
                d[k, k] = epsilon
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        Snew = gram_schmidt_rotation(F, Q, L)
        return Snew.T
    else:
        Snew = gram_schmidt_rotation(F, Q, prev)
        return Snew.T


def Potter(S_p, H, R, x_p, y):
    """
    Potter’s square-root update:
      S_p: prior square-root (m×m)
      H: measurement matrix (h×m)
      R: measurement noise cov (h×h)
      x_p: prior state (m×1)
      y: measurement (h×1)
    Returns (S_new, x_new).
    """
    x = x_p.copy()
    S = S_p.copy()
    I = np.eye(len(x))

    for i in range(H.shape[0]):
        H_i = H[i : i + 1]              # shape (1×m)
        y_i = y[i, 0]                   # scalar
        R_i = np.var(R[i])             # variance scalar
        Phi = S.T @ H_i.T               # (m×1)
        denom = (Phi.T @ Phi)[0, 0] + R_i
        if denom <= 0:
            a = 0.0
            gamma = 0.0
        else:
            a = 1.0 / denom
            gamma = a / (1.0 + math.sqrt(a * R_i))

        # Update S
        S = S @ (I - (Phi @ Phi.T) * (a * gamma))
        K = S @ Phi                     # (m×1)
        innov = y_i - float((H_i @ x)[0, 0])
        x = x + K * (a * innov)         # (m×1)

    return S, x


# --- Ensemble Kalman wrapper returning all 7 outputs ---

def ensamble_kalman(nameSignal, Fs, wC):
    m = len(wC)
    invertWC = np.where(wC == 1, 0, 1)
    sig = readSignal(nameSignal, Fs)
    H_all, H_sig, H_nsig = observation_matrices(m, 3, m - 3)

    n_sess = len(sig)
    resultAll      = np.zeros((n_sess, Fs))
    resultOriginal = np.zeros((n_sess, Fs))
    resultWC       = np.zeros((n_sess, Fs))
    resultNWC      = np.zeros((n_sess, Fs))
    yAll, yWC, yNWC = [], [], []

    # Initial full covariance and state
    P_all = np.cov(sig[0])
    P_sig = P_all.copy()
    P_nsig = P_all.copy()
    x_all = np.zeros((m, 1))
    x_sig = np.zeros((m, 1))
    x_nsig = np.zeros((m, 1))

    # Build initial transition matrices
    F0      = taylor_series(Fs, m)
    F0_sig  = F0.copy();  np.fill_diagonal(F0_sig,  wC)
    F0_nsig = F0.copy();  np.fill_diagonal(F0_nsig, invertWC)
    Q_eye   = np.eye(m)

    # Initial square-roots
    S_all  = getNextSquareRoot(P_all,  Q_eye, F0,      "initial")
    S_sig  = getNextSquareRoot(P_sig,  Q_eye, F0_sig,  "initial")
    S_nsig = getNextSquareRoot(P_nsig, Q_eye, F0_nsig, "initial")

    kind = "other"  # for subsequent updates

    for i, block in enumerate(sig):
        for j in range(Fs):
            # --- TIME UPDATE ---
            F      = taylor_series(Fs, m)
            F_sig  = F.copy();  np.fill_diagonal(F_sig,  wC)
            F_nsig = F.copy();  np.fill_diagonal(F_nsig, invertWC)

            xpt_all  = F @ x_all
            xpt_sig  = F_sig @ x_sig
            xpt_nsig = F_nsig @ x_nsig

            resultAll[i, j] = float(xpt_all.mean())
            resultWC[i, j]  = float(xpt_sig.mean())
            resultNWC[i, j] = float(xpt_nsig.mean())

            # --- MEASUREMENT “nextState” ---
            if j < Fs - 1:
                nextState = block[:, j + 1 : j + 2]
            else:
                if i < n_sess - 1:
                    nextState = sig[i + 1][:, 0 : 1]
                else:
                    nextState = sig[0][:, 0 : 1]
            resultOriginal[i, j] = float(nextState.mean())

            yAll.append(float(nextState.mean()))
            yWC.append(float((H_sig @ nextState).mean()))
            yNWC.append(float((H_nsig @ nextState).mean()))

            # --- NOISE COVARIANCES ---
            R_all  = noiseDiagCov(np.random.randn(m, m))
            R_sig  = noiseDiagCov(np.random.randn(3, 3))
            R_nsig = noiseDiagCov(np.random.randn(m - 3, m - 3))

            # --- COVARIANCE (square-root) TIME UPDATE ---
            S_all  = getNextSquareRoot(S_all,  Q_eye, F,      kind)
            S_sig  = getNextSquareRoot(S_sig,  Q_eye, F_sig,  kind)
            S_nsig = getNextSquareRoot(S_nsig, Q_eye, F_nsig, kind)

            # --- MEASUREMENT UPDATE (Potter) ---
            S_all,  x_all   = Potter(S_all,  H_all,  R_all,   xpt_all,       nextState)
            S_sig,  x_sig   = Potter(S_sig,  H_sig,  R_sig,   xpt_sig,       H_sig @ nextState)
            S_nsig, x_nsig  = Potter(S_nsig, H_nsig, R_nsig,  xpt_nsig,      H_nsig @ nextState)

            # Reconstruct full covariance if needed (not strictly required)
            P_all  = S_all  @ S_all.T
            P_sig  = S_sig  @ S_sig.T
            P_nsig = S_nsig @ S_nsig.T

            kind = "other"
        # end inner loop
    # end outer loop

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC


# Adapter for batch script

def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)


if __name__ == '__main__':
    # Avoid auto-running on import
    pass
