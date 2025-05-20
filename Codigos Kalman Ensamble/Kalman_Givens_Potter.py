# Kalman_Potter_Givens.py
import numpy as np
import math
import time
from scipy import linalg as lin

# (All helper functions identical to Potter+Gram–Schmidt, but default to method='givens')

def observation_matrices(m_all, m_significant, m_non_significant):
    H_all = np.eye(m_all)
    H_significant = np.zeros((m_significant, m_all))
    H_non_significant = np.zeros((m_non_significant, m_all))
    H_significant[0, -3] = 1
    H_significant[1, -2] = 1
    H_significant[2, -1] = 1
    for i in range(m_non_significant): H_non_significant[i,i]=1
    return H_all, H_significant, H_non_significant


def concatenateAmplitude(listSignal):
    return np.concatenate(listSignal, axis=None) if listSignal else np.zeros(0)

# Read EEG CSV into [sessions, sensors, samples]

def readSignal(path, samplingRate):
    data = np.genfromtxt(path, delimiter=',')
    data = np.delete(data, 0, axis=0)
    sessions = []
    for i in range(0, len(data)//samplingRate * samplingRate, samplingRate):
        sessions.append(data[i:i+samplingRate])
    return np.transpose(sessions, (0, 2, 1))

# Taylor series state transition

def taylor_series(Fs, m):
    C = np.zeros((m, m))
    for i in range(m):
        v = 1/(Fs**i)/math.factorial(i)
        row = np.full(m, v)
        np.fill_diagonal(C[i:], row)
    return C.T

def givens_rotation(F, Q, S):
    # same implementation as in Potter_GramShmidt
    m = S.shape[0]; U = np.vstack((S.T@F.T, np.sqrt(Q).T))
    for j in range(U.shape[1]):
        for i in range(U.shape[0]-1, j, -1):
            a, b = U[i-1,j], U[i,j]
            if b==0: c, s = 1,0
            else:
                if abs(b)>abs(a): r=a/b; s=1/np.sqrt(1+r*r); c=s*r
                else: r=b/a; c=1/np.sqrt(1+r*r); s=c*r
            G=np.eye(U.shape[0]); G[i-1,i-1],G[i-1,i],G[i,i-1],G[i,i]=c,s,-s,c
            U=G.T@U
    return U[:m,:m]

# (gram_schmidt_rotation unused)

def Potter(S_p, H, R, x_p, y):
    # identical to Potter above
    x, S = x_p, S_p; I=np.eye(len(x))
    for i in range(H.shape[0]):
        H_i = H[i:i+1]; y_i=y[i]; R_i=np.var(R[i]); Phi=S.T@H_i.T
        a=1/(Phi.T@Phi+R_i); gamma=a/(1+math.sqrt(a*R_i))
        S=S@(I-(Phi@Phi.T)*(a*gamma)); K=S@Phi; x=x+K*(a*(y_i-H_i@x))
    return S,x

# noiseDiagCov same as above

def noiseDiagCov(noise): D=np.zeros((noise.shape[0],)*2); np.fill_diagonal(D,[np.cov(noise[i])for i in range(noise.shape[0])]); return D

# getNextSquareRoot uses givens

def getNextSquareRoot(P,Q,F,kind,method='givens'):
    if kind=='initial': Pm=(P+P.T)/2; lu,d,_=lin.ldl(Pm,lower=True);L=lu@lin.fractional_matrix_power(d,0.5); return givens_rotation(F,Q,L).T
    return givens_rotation(F,Q,P).T

# Ensemble Kalman with Potter+Givens

def run(nameSignal,Fs,wC):
    m=len(wC); sig=readSignal(nameSignal,Fs)
    H_all,_,_=observation_matrices(m,3,m-3)
    x=np.zeros((m,1));P=np.cov(sig[0]);kind='initial';results=[]
    for session in sig:
        out=[]
        for j in range(Fs):
            F=taylor_series(Fs,m); x_pred=F@x
            S=getNextSquareRoot(P,np.eye(m),F,kind,'givens')
            noise=noiseDiagCov(np.random.randn(m,m));P,x=Potter(S,H_all,noise,x_pred,session[:,j:j+1])
            out.append(x_pred.mean());kind='other'
        results.append(out)
    return np.array(results)

if __name__=='__main__':
    import time;path='/Users/.../S1.csv';Fs=128;w=np.array([0,0,0,0,0,0,0,0,0,0,0,1,1,1])
    start=time.time();_ = run(path,Fs,w); print('Time:',time.time()-start)