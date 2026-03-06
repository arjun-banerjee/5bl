import os 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def retrieve(files):
    base = os.path.dirname(os.path.abspath(__file__))
    return [pd.read_csv(os.path.join(base,f)) for f in files], base

def undamped(t,A,w,phi,c):
    return A*np.cos(w*t+phi)+c

def undamped_fit(df):
    t = df[timecol].to_numpy(dtype=float)
    a = df[aycol].to_numpy(dtype=float)
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
    t = df[timecol].to_numpy(dtype=float)
    a = df[aycol].to_numpy(dtype=float)
    guesses = [np.ptp(a)/2, 0.05, 7.9, 0, np.mean(a)]
    popt, pcov = curve_fit(damped, t, a, p0=guesses, maxfev=10000)
    return t, a, popt, pcov

m = 0.2305
filenames = ["2.1_cleaned.csv", "2.2_cleaned.csv", "2.3_cleaned.csv", "2.4_cleaned.csv", "2.5_cleaned.csv", "2.6_cleaned.csv"]
timecol = "Time (s)"
aycol = "Ay (m/s²)"
dfs, base_dir = retrieve(filenames)

#undamped, all 6 plots
ks, sigma_ks = [],[]
ws, sigma_ws = [],[]

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

fig_undamped_res, axes_undamped_res = plt.subplots(2, 3, figsize=(15, 8))
axes_undamped_res = axes_undamped_res.flatten()

for ax, ax_res, df, fname in zip(axes, axes_undamped_res, dfs, filenames):
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
    
    predicted_a = undamped(t,*popt)
    residuals = a - predicted_a
    ax_res.scatter(t, residuals, color="darkred", s=10, alpha=0.7)
    ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5) # Baseline at y=0
    ax_res.set_title(f"Residuals for {fname}", fontsize=10)
    ax_res.set_xlabel("Time (s)")
    ax_res.set_ylabel("Residual Ay (m/s²)")
    ax_res.grid(True, linestyle="--", alpha=0.6)
fig.tight_layout()
save_path = os.path.join(base_dir, "2_undamped_fits.png")
fig.savefig(save_path, dpi=300, bbox_inches="tight")
fig_undamped_res.subplots_adjust(hspace=0.4)
fig_undamped_res.tight_layout()
save_path_undamped_res = os.path.join(base_dir, "2_undamped_residuals.png")
fig_undamped_res.savefig(save_path_undamped_res, dpi=300, bbox_inches="tight")
plt.show()

#damped, all 6 plots
betas, sigma_betas = [], []
omegas, sigma_omegas = [], []

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 8))
axes2 = axes2.flatten()

fig_damped_res, axes_res = plt.subplots(2, 3, figsize=(15, 8))
axes_res = axes_res.flatten()

for ax, ax_res, df, fname in zip(axes2, axes_res, dfs, filenames):
    t, a, popt, pcov = damped_fit(df)
    A, beta, w, phi, c = popt
    sigma_beta = float(np.sqrt(pcov[1, 1]))
    sigma_w = float(np.sqrt(pcov[2, 2]))
    betas.append(beta); sigma_betas.append(sigma_beta)
    omegas.append(w); sigma_omegas.append(sigma_w)
    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 1000)
    ax.plot(t_smooth, damped(t_smooth, *popt), label="Damped fit", color="mediumblue", linewidth=2)
    ax.set_title(f"{fname}\nω = {w:.3f} ± {sigma_w:.4f} | β = {beta:.5f} ± {sigma_beta:.5f}", fontsize=9)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

    predicted_a = damped(t, *popt)
    residuals = a - predicted_a
    ax_res.scatter(t, residuals, color="darkred", s=10, alpha=0.7)
    ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5) # Baseline
    ax_res.set_title(f"Damped Residuals: {fname}", fontsize=10)
    ax_res.set_xlabel("Time (s)")
    ax_res.set_ylabel("Residual Ay (m/s²)")
    ax_res.grid(True, linestyle="--", alpha=0.6)

fig2.tight_layout()
save_path_fits = os.path.join(base_dir, "2_damped_accel_fits.png")
fig2.savefig(save_path_fits, dpi=300, bbox_inches="tight")
fig_damped_res.tight_layout()
save_path_res = os.path.join(base_dir, "2_damped_residuals.png")
fig_damped_res.savefig(save_path_res, dpi=300, bbox_inches="tight")
plt.show()

#dataset 1.3 comparison grid
df23 = dfs[filenames.index("2.3_cleaned.csv")]
t_u, a_u, popt_u, pcov_u = undamped_fit(df23)
k_u, sigma_k_u, w_u, sigma_w_u = undamped_k_uncertainty(popt_u, pcov_u, m)
predicted_u = undamped(t_u, *popt_u)
residuals_u = a_u - predicted_u

t_d, a_d, popt_d, pcov_d = damped_fit(df23)
A_d, beta_d, w_d, phi_d, c_d = popt_d
sigma_beta_d = float(np.sqrt(pcov_d[1, 1]))
sigma_w_d = float(np.sqrt(pcov_d[2, 2]))

k_d = m*(w_d**2+beta_d**2)
sigma_k_d = 2*m*w_d*sigma_w_d 

predicted_d = damped(t_d, *popt_d)
residuals_d = a_d - predicted_d

fig_comp, axs_comp = plt.subplots(2, 2, figsize=(14, 10))

axs_comp[0, 0].scatter(t_u, a_u, label="Raw Data", color="gray", s=10, alpha=0.7)
t_smooth_u = np.linspace(t_u.min(), t_u.max(), 1000)
axs_comp[0, 0].plot(t_smooth_u, undamped(t_smooth_u, *popt_u), label="Undamped Fit", color="red", linewidth=2)
axs_comp[0, 0].set_title(f"Undamped Fit, k = {k_u:.4f} ± {sigma_k_u:.4f} N/m  |  ω = {w_u:.4f} ± {sigma_w_u:.4f} rad/s")
axs_comp[0, 0].set_xlabel("Time (s)")
axs_comp[0, 0].set_ylabel("Ay (m/s²)")
axs_comp[0, 0].grid(True, linestyle="--", alpha=0.6)
axs_comp[0, 0].legend(loc="upper right")

axs_comp[0, 1].scatter(t_u, residuals_u, color="darkred", s=10, alpha=0.7)
axs_comp[0, 1].axhline(0, color="black", linestyle="--", linewidth=1.5)
axs_comp[0, 1].set_title(f"Undamped Residuals")
axs_comp[0, 1].set_xlabel("Time (s)")
axs_comp[0, 1].set_ylabel("Residual Ay (m/s²)")
axs_comp[0, 1].grid(True, linestyle="--", alpha=0.6)

axs_comp[1, 0].scatter(t_d, a_d, label="Raw Data", color="gray", s=10, alpha=0.7)
t_smooth_d = np.linspace(t_d.min(), t_d.max(), 1000)
axs_comp[1, 0].plot(t_smooth_d, damped(t_smooth_d, *popt_d), label="Damped Fit", color="mediumblue", linewidth=2)
axs_comp[1, 0].set_title(f"Damped Fit, k = {k_d:.4f} ± {sigma_k_d:.4f} N/m  |  ω = {w_d:.5f} ± {sigma_w_d:.5f} rad/s  |  β = {beta_d:.5f} ± {sigma_beta_d:.5f} s⁻¹")
axs_comp[1, 0].set_xlabel("Time (s)")
axs_comp[1, 0].set_ylabel("Ay (m/s²)")
axs_comp[1, 0].grid(True, linestyle="--", alpha=0.6)
axs_comp[1, 0].legend(loc="upper right")

axs_comp[1, 1].scatter(t_d, residuals_d, color="purple", s=10, alpha=0.7)
axs_comp[1, 1].axhline(0, color="black", linestyle="--", linewidth=1.5)
axs_comp[1, 1].set_title(f"Damped Residuals")
axs_comp[1, 1].set_xlabel("Time (s)")
axs_comp[1, 1].set_ylabel("Residual Ay (m/s²)")
axs_comp[1, 1].grid(True, linestyle="--", alpha=0.6)

fig_comp.tight_layout()
fig_comp.subplots_adjust(hspace=0.3)
save_path_comp = os.path.join(base_dir, "2.3_comparison_grid.png")
fig_comp.savefig(save_path_comp, dpi=300, bbox_inches="tight")
plt.show()

ax = df23.plot(x="Time (s)", y=["Ay (m/s²)", "Fᵧ (N)"], subplots=True, figsize=(10, 6), grid=True, title="Acceleration and Force (2.3_cleaned.csv)")
ax[0].set_ylabel("Ay (m/s²)"); ax[1].set_ylabel("Fᵧ (N)")
plt.savefig(os.path.join(base_dir, "2.3_accel_vs_force.png"), dpi=300, bbox_inches="tight")
plt.show()