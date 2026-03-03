import os 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

m = 0.2305
tmax = 6
filenames = ["2.1_cleaned.csv", "2.2_cleaned.csv", "2.3_cleaned.csv", "2.4_cleaned.csv", "2.5_cleaned.csv", "2.6_cleaned.csv"]
timecol = "Time (s)"
aycol = "Ay (m/s²)"

def retrieve(files):
    base = os.path.dirname(os.path.abspath(__file__))
    return [pd.read_csv(os.path.join(base,f)) for f in files], base

###undamped

def undamped(t,A,w,phi,c):
    return A*np.cos(w*t+phi)+c

def undamped_fit(df):
    df_fit = df[df[timecol] <= tmax]
    t = df_fit[timecol].to_numpy(dtype=float)
    a = df_fit[aycol].to_numpy(dtype=float)
    initial_guesses = [np.ptp(a)/2,2*np.pi/0.86,0,np.mean(a)]
    popt,pcov = curve_fit(undamped,t,a,p0=initial_guesses)
    return t,a,popt,pcov

def undamped_k(w,m):
    return m*w**2

def undamped_k_uncertainty(popt,pcov,m):
    w = popt[1]
    sigma_w = float(np.sqrt(pcov[1, 1]))
    k = undamped_k(w,m)
    sigma_k = 2 * m * w * sigma_w
    return k, sigma_k, w, sigma_w

def weighted_mean(values, sigmas):
    values = np.asarray(values, dtype=float)
    sigmas = np.asarray(sigmas, dtype=float)
    mask = np.isfinite(values) & np.isfinite(sigmas) & (sigmas > 0)
    values, sigmas = values[mask], sigmas[mask]
    if len(values) == 0:
        return np.nan, np.nan
    wts = 1.0 / sigmas**2
    mean = np.sum(wts * values) / np.sum(wts)
    sigma_mean = np.sqrt(1.0 / np.sum(wts))
    return float(mean), float(sigma_mean)

dfs, base_dir = retrieve(filenames)
ks, sigma_ks = [],[]
ws, sigma_ws = [],[]

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for ax, df, fname in zip(axes, dfs, filenames):
    t, a, popt, pcov = undamped_fit(df)
    k, sigma_k, w, sigma_w = undamped_k_uncertainty(popt, pcov, m)
    ks.append(k); sigma_ks.append(sigma_k)
    ws.append(w); sigma_ws.append(sigma_w)

    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 500)
    ax.plot(t_smooth, undamped(t_smooth, *popt), label="Fitted Curve", color="red", linewidth=2)
    ax.set_title(f"{fname} | k = {k:.2f} ± {sigma_k:.3f} N/m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

plt.tight_layout()
save_path = os.path.join(base_dir, "2_undamped_fits.png")
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

k_wmean, k_wsigma = weighted_mean(ks, sigma_ks)
print(f"\nWeighted mean k: {k_wmean:.3f} ± {k_wsigma:.3f} N/m")

###damped
def damped(t,A,beta,w,phi,c):
    return A*np.exp(-beta*t)*(beta**2 - w**2)*np.cos(w*t + phi) + 2*beta*w*np.sin(w*t + phi)+ c

def damped_fit(df):
    