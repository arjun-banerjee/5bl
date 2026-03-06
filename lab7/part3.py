#imports
import os 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#functions
def retrieve(files):
    base = os.path.dirname(os.path.abspath(__file__))
    return [pd.read_csv(os.path.join(base, f)) for f in files], base

def undamped(t,A,w,phi,c):
    return A*np.cos(w*t+phi)+c

def undamped_fit(df):
    t = df["Time (s)"].to_numpy(dtype=float)
    a = (df["Fᵧ (N)"]/m).to_numpy(dtype=float)
    guesses = [np.ptp(a)/2,7.9,0,np.mean(a)]
    popt,pcov = curve_fit(undamped,t,a,p0=guesses)
    return t,a,popt,pcov

def undamped_k(w,m):
    return m*w**2

def undamped_k_uncertainty(popt,pcov,m):
    w = popt[1]
    sigma_w = float(np.sqrt(pcov[1, 1]))
    k = undamped_k(w,m)
    sigma_k = 2*m*w*sigma_w
    return k, sigma_k, w, sigma_w

def damped(t, A, beta, w, phi, c):
    return A * np.exp(-beta * t) * ((beta**2 - w**2) * np.cos(w * t + phi) + 2 * beta * w * np.sin(w * t + phi)) + c

def damped_fit(df):
    t = df["Time (s)"].to_numpy(dtype=float)
    a = (df["Fᵧ (N)"]/m).to_numpy(dtype=float)
    guesses = [np.ptp(a)/2, 0.05, 7.9, 0, np.mean(a)]
    popt, pcov = curve_fit(damped, t, a, p0=guesses, maxfev=10000)
    return t, a, popt, pcov

#setup
m=0.2035
filenames = ["3.1.csv", "3.2.csv", "3.3.csv", "3.4.csv", "3.5.csv", "3.6.csv"]
dfs, base_dir = retrieve(filenames)

#Force grid for the datasets
fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
for ax, df, fname in zip(axes.flatten(), dfs, filenames):
    ax.plot(df["Time (s)"], df["Fᵧ (N)"], color="mediumblue", linewidth=1.5)
    ax.set_title(fname, fontsize=12)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
fig.suptitle("Force vs. Time", fontsize=16, fontweight="bold")
plt.savefig(os.path.join(base_dir, "3_force_grid.png"), dpi=300)
plt.show()

#All measurements for dataset
ax = dfs[-1].plot(x="Time (s)", y=["Fᵧ (N)","rᵧ (m)","vᵧ (m/s)","aᵧ (m/s²)"], subplots=True, figsize=(10, 6), grid=True, title="Force, Wheel Position, Velocity, and Acceleration  (3.2_cleaned.csv)")
ax[0].set_ylabel("Fᵧ (N)"); ax[1].set_ylabel("rᵧ (m)"); ax[2].set_ylabel("vᵧ (m/s)"); ax[3].set_ylabel("aᵧ (m/s²)")
plt.savefig(os.path.join(base_dir, "3.2_measurements.png"), dpi=300, bbox_inches="tight")
plt.show()

#Fit data to undamped (1), display w
df_32 = dfs[1]

t_32, a_32, popt_32, pcov_32 = undamped_fit(df_32)
w_32 = popt_32[1]
sigma_w_32 = float(np.sqrt(pcov_32[1, 1]))
t_smooth_32 = np.linspace(t_32.min(), t_32.max(), 1000)
fit_32 = undamped(t_smooth_32, *popt_32)
residuals_32 = a_32 - undamped(t_32, *popt_32)

fig3, (ax_fit, ax_res) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax_fit.scatter(t_32, a_32, label="Raw Data (Derived Accel)", color="gray", s=10, alpha=0.7)
ax_fit.plot(t_smooth_32, fit_32, label="Undamped Fit", color="red", linewidth=2)
ax_fit.set_title(f"Undamped Fit (3.2.csv) | ω = {w_32:.3f} ± {sigma_w_32:.3f} rad/s", fontsize=14, fontweight="bold")
ax_fit.set_ylabel("Acceleration (m/s²)", fontsize=12)
ax_fit.grid(True, linestyle="--", alpha=0.6)
ax_fit.legend(loc="upper right")


ax_res.scatter(t_32, residuals_32, color="darkred", s=10, alpha=0.7)
ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5)
ax_res.set_title("Residuals", fontsize=12)
ax_res.set_xlabel("Time (s)", fontsize=12)
ax_res.set_ylabel("Residual Ay (m/s²)", fontsize=12)
ax_res.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(base_dir, "3.2_undamped_fit_and_residuals.png"), dpi=300)
plt.show()

#Fit data to velocity-damped (2), display w and b
t_32_d, a_32_d, popt_32_d, pcov_32_d = damped_fit(df_32)

beta_32 = popt_32_d[1]
sigma_beta_32 = float(np.sqrt(pcov_32_d[1, 1]))
w_32_d = popt_32_d[2]
sigma_w_32_d = float(np.sqrt(pcov_32_d[2, 2]))


t_smooth_32_d = np.linspace(t_32_d.min(), t_32_d.max(), 1000)
fit_32_d = damped(t_smooth_32_d, *popt_32_d)
residuals_32_d = a_32_d - damped(t_32_d, *popt_32_d)

fig4, (ax_fit_d, ax_res_d) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax_fit_d.scatter(t_32_d, a_32_d, label="Raw Data (Derived Accel)", color="gray", s=10, alpha=0.7)
ax_fit_d.plot(t_smooth_32_d, fit_32_d, label="Damped Fit", color="darkorange", linewidth=2)
ax_fit_d.set_title(f"Damped Fit (3.2.csv) | ω = {w_32_d:.3f} ± {sigma_w_32_d:.3f} rad/s, β = {beta_32:.3f} ± {sigma_beta_32:.3f} s⁻¹", fontsize=13, fontweight="bold")
ax_fit_d.set_ylabel("Acceleration (m/s²)", fontsize=12)
ax_fit_d.grid(True, linestyle="--", alpha=0.6)
ax_fit_d.legend(loc="upper right")


ax_res_d.scatter(t_32_d, residuals_32_d, color="darkred", s=10, alpha=0.7)
ax_res_d.axhline(0, color="black", linestyle="--", linewidth=1.5)
ax_res_d.set_title("Residuals", fontsize=12)
ax_res_d.set_xlabel("Time (s)", fontsize=12)
ax_res_d.set_ylabel("Residual Ay (m/s²)", fontsize=12)
ax_res_d.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(base_dir, "3.2_damped_fit_and_residuals.png"), dpi=300)
plt.show()