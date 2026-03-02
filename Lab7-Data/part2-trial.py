import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# -----------------------------
# Config
# -----------------------------
m = 0.2305

# Undamped: keep your cap (you can change this)
tmax_undamped = 6

# Damped: USE ALL DATA (no cap)
tmax_damped = None

filenames = ["2.1_cleaned.csv", "2.2_cleaned.csv", "2.3_cleaned.csv",
             "2.4_cleaned.csv", "2.5_cleaned.csv", "2.6_cleaned.csv"]
timecol = "Time (s)"
aycol = "Ay (m/s²)"

# -----------------------------
# Utilities
# -----------------------------
def retrieve(files):
    base = os.path.dirname(os.path.abspath(__file__))
    return [pd.read_csv(os.path.join(base, f)) for f in files], base

def slice_time(df, tmax):
    if tmax is None:
        return df
    return df[df[timecol] <= tmax]

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

# -----------------------------
# Undamped fit
# -----------------------------
def undamped(t, A, w, phi, c):
    return A * np.cos(w * t + phi) + c

def undamped_fit(df, tmax=tmax_undamped):
    df_fit = slice_time(df, tmax)
    t = df_fit[timecol].to_numpy(dtype=float)
    a = df_fit[aycol].to_numpy(dtype=float)

    A0 = 0.5 * np.ptp(a) if np.ptp(a) > 0 else 1.0
    w0 = 2 * np.pi / 0.86
    phi0 = 0.0
    c0 = float(np.mean(a))
    p0 = [A0, w0, phi0, c0]

    bounds = ([-np.inf, 0.0, -2*np.pi, -np.inf],
              [ np.inf, np.inf,  2*np.pi,  np.inf])

    popt, pcov = curve_fit(undamped, t, a, p0=p0, bounds=bounds, maxfev=20000)
    return t, a, popt, pcov

def undamped_k(w, m):
    return m * w**2

def undamped_k_uncertainty(popt, pcov, m):
    w = float(popt[1])
    sigma_w = float(np.sqrt(pcov[1, 1]))
    k = undamped_k(w, m)
    sigma_k = 2 * m * w * sigma_w
    return k, sigma_k, w, sigma_w

# -----------------------------
# Damped fit (USE ALL DATA)
# a(t) = A e^{-βt}[(β^2-ω^2)cos(ωt+φ) + 2βω sin(ωt+φ)] + c
# -----------------------------
def damped_accel(t, A, beta, w, phi, c):
    return A*np.exp(-beta*t)*(
        (beta**2 - w**2)*np.cos(w*t + phi) + 2*beta*w*np.sin(w*t + phi)
    ) + c

def damped_fit(df, tmax=tmax_damped):
    df_fit = slice_time(df, tmax)  # tmax=None -> no slicing
    t = df_fit[timecol].to_numpy(dtype=float)
    a = df_fit[aycol].to_numpy(dtype=float)

    # Seed ω, φ, c from undamped fit (still OK even if undamped uses t<=6)
    _, _, popt_u, _ = undamped_fit(df, tmax=tmax_undamped)
    A0 = float(abs(popt_u[0])) if np.isfinite(popt_u[0]) else 1.0
    w0 = float(popt_u[1]) if np.isfinite(popt_u[1]) else 2*np.pi/0.86
    phi0 = float(popt_u[2]) if np.isfinite(popt_u[2]) else 0.0
    c0 = float(popt_u[3]) if np.isfinite(popt_u[3]) else float(np.mean(a))

    beta0 = 0.05
    p0 = [A0, beta0, w0, phi0, c0]

    bounds = ([-np.inf, 0.0, 0.0, -2*np.pi, -np.inf],
              [ np.inf, np.inf, np.inf,  2*np.pi,  np.inf])

    popt, pcov = curve_fit(damped_accel, t, a, p0=p0, bounds=bounds, maxfev=50000)
    return t, a, popt, pcov

def damped_k(beta, w, m):
    return m * (w**2 + beta**2)

def damped_k_uncertainty(popt, pcov, m):
    beta = float(popt[1])
    w = float(popt[2])

    k = damped_k(beta, w, m)

    var_beta = float(pcov[1, 1])
    var_w = float(pcov[2, 2])
    cov_bw = float(pcov[1, 2])  # = pcov[2,1]

    dk_db = 2 * m * beta
    dk_dw = 2 * m * w

    var_k = (dk_db**2)*var_beta + (dk_dw**2)*var_w + 2*dk_db*dk_dw*cov_bw
    sigma_k = float(np.sqrt(var_k)) if var_k >= 0 else np.nan

    return k, sigma_k, beta, np.sqrt(var_beta), w, np.sqrt(var_w)

# -----------------------------
# Run: Undamped
# -----------------------------
dfs, base_dir = retrieve(filenames)

ks, sigma_ks = [], []
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for ax, df, fname in zip(axes, dfs, filenames):
    t, a, popt, pcov = undamped_fit(df, tmax=tmax_undamped)
    k, sigma_k, w, sigma_w = undamped_k_uncertainty(popt, pcov, m)

    ks.append(k); sigma_ks.append(sigma_k)

    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 500)
    ax.plot(t_smooth, undamped(t_smooth, *popt), label="Fitted Curve", color="red", linewidth=2)
    ax.set_title(f"{fname} | k = {k:.2f} ± {sigma_k:.3f} N/m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

plt.tight_layout()
plt.savefig(os.path.join(base_dir, "2_undamped_fits.png"), dpi=300, bbox_inches="tight")
plt.show()

k_wmean, k_wsigma = weighted_mean(ks, sigma_ks)
print(f"\nUndamped weighted mean k: {k_wmean:.3f} ± {k_wsigma:.3f} N/m")

# -----------------------------
# Run: Damped (ALL DATA)
# -----------------------------
kds, sigma_kds = [], []
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for ax, df, fname in zip(axes, dfs, filenames):
    t, a, popt, pcov = damped_fit(df, tmax=tmax_damped)  # None -> all data
    k, sigma_k, beta, sigma_beta, w, sigma_w = damped_k_uncertainty(popt, pcov, m)

    kds.append(k); sigma_kds.append(sigma_k)

    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 500)
    ax.plot(t_smooth, damped_accel(t_smooth, *popt), label="Damped accel fit", color="blue", linewidth=2)

    ax.set_title(f"{fname} | k = {k:.2f} ± {sigma_k:.3f} N/m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

plt.tight_layout()
plt.savefig(os.path.join(base_dir, "2_damped_accel_fits.png"), dpi=300, bbox_inches="tight")
plt.show()

kd_wmean, kd_wsigma = weighted_mean(kds, sigma_kds)
print(f"\nDamped weighted mean k (all data): {kd_wmean:.4f} ± {kd_wsigma:.4f} N/m")