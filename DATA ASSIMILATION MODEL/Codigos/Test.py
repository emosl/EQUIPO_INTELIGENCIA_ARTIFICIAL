from scipy.signal import welch
from scipy.stats import wilcoxon


def Welch(signal, fs=128):
    f, Pxx = welch(signal, fs=fs)
    return f, Pxx

def Wilcoxon(signal1, signal2):
    statistic, Pvalue = wilcoxon(signal1, signal2)
    return statistic, Pvalue

