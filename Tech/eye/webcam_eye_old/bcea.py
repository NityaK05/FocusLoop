# bcea.py
import numpy as np
from scipy.stats import chi2

def compute_bcea(xs, ys, p_val=0.95):
    xs, ys = np.asarray(xs), np.asarray(ys)
    if xs.size < 2:
        return 0.0
    cov = np.cov(xs, ys)
    σx, σy = np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])
    ρ = cov[0, 1] / (σx * σy + 1e-12)
    χ2_val = chi2.ppf(p_val, df=2)
    return 2 * np.pi * χ2_val * σx * σy * np.sqrt(1 - ρ**2)

def normalize_bcea(bcea, baseline):
    if baseline <= 0:
        raise ValueError("Baseline must be > 0")
    return float(np.clip(bcea / baseline, 0.0, 1.0))
