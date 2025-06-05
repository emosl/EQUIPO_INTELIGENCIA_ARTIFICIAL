# Kalman_GramSchmidt_Bierman_fixed.py
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
    """Build the m×m Taylor‐series state‐transition matrix."""
    C = np.zeros((m, m))
    for i in range(m):
        v = 1.0 / (Fs**i) / math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T

def gram_schmidt_rotation(F, Q, S):
    """Compute square‐root time‐update via QR decomposition."""
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

def getNextSquareRoot(prev, Q, F, kind):
    """
    Returns the next square‐root of covariance using Gram–Schmidt.
    If kind == 'initial', prev is full covariance P:
      - Symmetrize, LDL ⇒ L·D·Lᵀ, clamp D ≥ ε, form L·D^{½}, then QR.
    If kind == 'other', prev is the prior square‐root S: directly QR.
    """
    epsilon = 1e-12
    if kind == 'initial':
        Pm = (prev + prev.T) / 2.0
        lu, d, _ = lin.ldl(Pm, lower=True)
        # clamp diagonal of d
        for k in range(d.shape[0]):
            if d[k, k] < epsilon:
                d[k, k] = epsilon
        L = lu @ lin.fractional_matrix_power(d, 0.5)
        Snew = gram_schmidt_rotation(F, Q, L)
        return Snew.T
    else:
        Snew = gram_schmidt_rotation(F, Q, prev)
        return Snew.T

def bierman_update(S_p, H, R, x_p, y):
    """
    UD-based Bierman measurement update.
    Returns updated sqrt covariance S_t and state x_t.
    """
    epsilon = 1e-12
    P_p = S_p @ S_p.T
    n = P_p.shape[0]
    D = np.diag(P_p).copy()
    U = np.eye(n)
    # build U from P_p = U·diag(D)·Uᵀ
    for i in range(n):
        for j in range(i):
            U[i, j] = P_p[i, j] / D[j]
    # sequential update
    for k in range(H.shape[0]):
        Hi = H[k : k + 1]      # (1×n)
        yi = y[k, 0]           # scalar
        Ri = R[k, k]           # scalar variance

        phi = Hi @ U           # (1×n)
        c = (D * phi.ravel()).reshape(n, 1)  # (n×1)
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

    # Initial full covariance & state
    P_all = np.cov(sig[0])
    P_sig = P_all.copy()
    P_nsig = P_all.copy()
    x_all = np.zeros((m, 1))
    x_sig = np.zeros((m, 1))
    x_nsig = np.zeros((m, 1))

    # Initial transition matrices
    F0      = taylor_series(Fs, m)
    F0_sig  = F0.copy();   np.fill_diagonal(F0_sig,  wC)
    F0_nsig = F0.copy();   np.fill_diagonal(F0_nsig, invertWC)
    Q_eye   = np.eye(m)

    # Initial square‐roots via Gram–Schmidt
    S_all  = getNextSquareRoot(P_all,  Q_eye, F0,      'initial')
    S_sig  = getNextSquareRoot(P_sig,  Q_eye, F0_sig,  'initial')
    S_nsig = getNextSquareRoot(P_nsig, Q_eye, F0_nsig, 'initial')

    kind = 'other'  # for subsequent updates

    for i, block in enumerate(sig):
        for j in range(Fs):
            # --- TIME UPDATE ---
            F      = taylor_series(Fs, m)
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

            # --- SQUARE‐ROOT (Gram–Schmidt) TIME UPDATE ---
            S_all  = getNextSquareRoot(S_all,  Q_eye, F,      kind)
            S_sig  = getNextSquareRoot(S_sig,  Q_eye, F_sig,  kind)
            S_nsig = getNextSquareRoot(S_nsig, Q_eye, F_nsig, kind)

            # --- MEASUREMENT UPDATE (Bierman UD) ---
            S_all,  x_all   = bierman_update(S_all,  H_all,  R_all,   xpt_all,       nextState)
            S_sig,  x_sig   = bierman_update(S_sig,  H_sig,  R_sig,   xpt_sig,       H_sig @ nextState)
            S_nsig, x_nsig  = bierman_update(S_nsig, H_nsig, R_nsig,  xpt_nsig,      H_nsig @ nextState)

            # Reconstruct covariance if needed
            P_all  = S_all @ S_all.T
            P_sig  = S_sig @ S_sig.T
            P_nsig = S_nsig @ S_nsig.T

            kind = 'other'
        # end inner loop
    # end outer loop

    return resultAll, resultOriginal, resultWC, resultNWC, yAll, yWC, yNWC

def run(nameSignal, Fs, wC):
    return ensamble_kalman(nameSignal, Fs, wC)

if __name__ == '__main__':
    # Prevent auto‐execution on import
    pass
