#imports
import os 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

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

def constant_friction_fit(df,threshold=0.005):
    t_pos = df["Time (s)"].to_numpy(dtype=float)
    pos = df["rᵧ (m)"].to_numpy(dtype=float)
    tail_idx = int(len(pos) * 0.9)
    y_eq = np.mean(pos[tail_idx:])
    peaks, _ = find_peaks(pos, prominence=threshold)
    valleys, _ = find_peaks(-pos, prominence=threshold)
    all_turning_indices = np.sort(np.concatenate((peaks, valleys)))
    amplitudes = np.abs(pos[all_turning_indices] - y_eq)
    n_values = np.arange(len(amplitudes))
    popt_cf = np.polyfit(n_values, amplitudes, 1) 
    return t_pos, pos, n_values, amplitudes, popt_cf, all_turning_indices, y_eq

#setup
m=0.2035
filenames = ["3.1_cleaned.csv", "3.2_cleaned.csv", "3.3_cleaned.csv", "3.4_cleaned.csv", "3.5_cleaned.csv", "3.6_cleaned.csv"]
dfs, base_dir = retrieve(filenames)

#Force grid for the datasets
fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
for ax, df, fname in zip(axes.flatten(), dfs, filenames):
    ax.plot(df["Time (s)"], df["Fᵧ (N)"], color="mediumblue", linewidth=1.5)
    ax.set_title(fname, fontsize=12)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Fy (m/s²)")
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

#Fit data to constant friction (3)
t_pos, pos, n_values, amplitudes, popt_cf, turning_indices, y_eq = constant_friction_fit(df_32)
m_slope, b_intercept = popt_cf
fit_amplitudes = m_slope * n_values + b_intercept
residuals_cf = amplitudes - fit_amplitudes

fig5, (ax_pos, ax_amp, ax_res) = plt.subplots(3, 1, figsize=(10, 12), constrained_layout=True)

ax_pos.plot(t_pos, pos, label="Position (rᵧ)", color="mediumseagreen", linewidth=1.5)
ax_pos.axhline(y_eq, color="black", linestyle="--", label="Equilibrium", alpha=0.7)
ax_pos.plot(t_pos[turning_indices], pos[turning_indices], 'ko', markersize=4, label="Turning Points")
ax_pos.set_title("Wheel Position vs Time with Identified Turning Points", fontsize=13, fontweight="bold")
ax_pos.set_ylabel("Position (m)", fontsize=12)
ax_pos.grid(True, linestyle="--", alpha=0.6)
ax_pos.legend(loc="upper right")

ax_amp.plot(n_values, amplitudes, 'bo', label="Calculated Amplitudes (Aₙ)")
ax_amp.plot(n_values, fit_amplitudes, 'r-', linewidth=2, label=f"Linear Fit (Slope = {m_slope:.5f} m/peak)")
ax_amp.set_title("Amplitude Decay Sequence (Constant Friction)", fontsize=13, fontweight="bold")
ax_amp.set_ylabel("Amplitude |rᵧ - y_eq| (m)", fontsize=12)
ax_amp.grid(True, linestyle="--", alpha=0.6)
ax_amp.legend(loc="upper right")

ax_res.scatter(n_values, residuals_cf, color="darkred", s=30, alpha=0.8, label="Residuals")
ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5)
ax_res.set_title("Residuals of Linear Fit", fontsize=13, fontweight="bold")
ax_res.set_xlabel("Peak Number (n)", fontsize=12)
ax_res.set_ylabel("Residual Amplitude (m)", fontsize=12)
ax_res.grid(True, linestyle="--", alpha=0.6)
ax_res.legend(loc="upper right")

plt.savefig(os.path.join(base_dir, "3.2_constant_friction_fit.png"), dpi=300)
plt.show()