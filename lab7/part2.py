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

# Figure 1: The main undamped fits
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

# Figure 2: The undamped residuals
fig_undamped_res, axes_undamped_res = plt.subplots(2, 3, figsize=(15, 8))
axes_undamped_res = axes_undamped_res.flatten()

for ax, ax_res, df, fname in zip(axes, axes_undamped_res, dfs, filenames):
    t, a, popt, pcov = undamped_fit(df)
    k, sigma_k, w, sigma_w = undamped_k_uncertainty(popt, pcov, m)
    ks.append(k); sigma_ks.append(sigma_k)
    ws.append(w); sigma_ws.append(sigma_w)

    # --- 1. Main Fit Plot ---
    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 500)
    ax.plot(t_smooth, undamped(t_smooth, *popt), label="Fitted Curve", color="red", linewidth=2)
    ax.set_title(f"{fname} | k = {k:.2f} ± {sigma_k:.3f} N/m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

    # --- 2. Residual Plot ---
    # Residuals = Actual Data - Predicted Data
    predicted_a = undamped(t, *popt)
    residuals = a - predicted_a
    
    ax_res.scatter(t, residuals, color="darkred", s=10, alpha=0.7)
    ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5) # Baseline at y=0
    
    ax_res.set_title(f"Residuals for {fname}", fontsize=10)
    ax_res.set_xlabel("Time (s)")
    ax_res.set_ylabel("Residual Ay (m/s²)")
    ax_res.grid(True, linestyle="--", alpha=0.6)

# Finalize and save the main fits figure
fig.tight_layout()
save_path = os.path.join(base_dir, "2_undamped_fits.png")
fig.savefig(save_path, dpi=300, bbox_inches="tight")

# Finalize and save the residuals figure
fig_undamped_res.subplots_adjust(hspace=0.4)
fig_undamped_res.tight_layout()
save_path_undamped_res = os.path.join(base_dir, "2_undamped_residuals.png")
fig_undamped_res.savefig(save_path_undamped_res, dpi=300, bbox_inches="tight")

plt.show()

k_wmean, k_wsigma = weighted_mean(ks, sigma_ks)
print(f"\nWeighted mean k: {k_wmean:.3f} ± {k_wsigma:.3f} N/m")

### damped
def damped(t, A, beta, w, phi, c):
    # Exponential decay applied to both terms, plus an offset c
    return A * np.exp(-beta * t) * ((beta**2 - w**2) * np.cos(w * t + phi) + 2 * beta * w * np.sin(w * t + phi)) + c

def damped_fit(df):
    # Using the full dataset (no tmax cutoff)
    t = df[timecol].to_numpy(dtype=float)
    a = df[aycol].to_numpy(dtype=float)
    
    # Initial guesses
    A_guess = np.ptp(a) / 2
    w_guess = 7.9  # Approx w based on k ~ 14.4 N/m and m = 0.2305 kg
    beta_guess = 0.05 # Small initial decay factor
    phi_guess = 0
    c_guess = np.mean(a)
    
    initial_guesses = [A_guess, beta_guess, w_guess, phi_guess, c_guess]
    
    # Fit curve (increased maxfev for better convergence on full datasets)
    popt, pcov = curve_fit(damped, t, a, p0=initial_guesses, maxfev=10000)
    return t, a, popt, pcov

# --- Plotting and Analysis for Damped Data ---
betas, sigma_betas = [], []
omegas, sigma_omegas = [], []

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 8))
axes2 = axes2.flatten()

for ax, df, fname in zip(axes2, dfs, filenames):
    t, a, popt, pcov = damped_fit(df)
    A, beta, w, phi, c = popt
    
    # Extract uncertainties from covariance matrix diagonals
    sigma_beta = float(np.sqrt(pcov[1, 1]))
    sigma_w = float(np.sqrt(pcov[2, 2]))
    
    betas.append(beta)
    sigma_betas.append(sigma_beta)
    omegas.append(w)
    sigma_omegas.append(sigma_w)
    
    # Plotting
    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    
    # Smooth curve for plotting
    t_smooth = np.linspace(t.min(), t.max(), 1000)
    ax.plot(t_smooth, damped(t_smooth, *popt), label="Damped accel fit", color="mediumblue", linewidth=2)
    
    # Split title into two lines (\n) and added a decimal place to uncertainties
    ax.set_title(f"{fname}\nω = {w:.3f} ± {sigma_w:.4f} rad/s  |  β = {beta:.5f} ± {sigma_beta:.5f} s⁻¹", fontsize=10)
    
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

# Adjust spacing so the two-line titles don't get cut off or overlap the graphs
plt.subplots_adjust(hspace=0.4) 
plt.tight_layout()

save_path_damped = os.path.join(base_dir, "2_damped_accel_fits.png")
plt.savefig(save_path_damped, dpi=300, bbox_inches="tight")
plt.show()
fig_undamped_res.savefig(os.path.join(base_dir, "2_undamped_residuals.png"), dpi=300, bbox_inches="tight")

# Calculate and print the weighted means
beta_wmean, beta_wsigma = weighted_mean(betas, sigma_betas)
w_wmean, w_wsigma = weighted_mean(omegas, sigma_omegas)

print(f"\n--- Damped Results ---")
print(f"Weighted mean beta (β): {beta_wmean:.5f} ± {beta_wsigma:.5f} s⁻¹")
print(f"Weighted mean omega (ω): {w_wmean:.5f} ± {w_wsigma:.5f} rad/s")### damped
def damped(t, A, beta, w, phi, c):
    # Exponential decay applied to both terms, plus an offset c
    return A * np.exp(-beta * t) * ((beta**2 - w**2) * np.cos(w * t + phi) + 2 * beta * w * np.sin(w * t + phi)) + c

def damped_fit(df):
    # Using the full dataset (no tmax cutoff)
    t = df[timecol].to_numpy(dtype=float)
    a = df[aycol].to_numpy(dtype=float)
    
    # Initial guesses
    A_guess = np.ptp(a) / 2
    w_guess = 7.9  # Approx w based on k ~ 14.4 N/m and m = 0.2305 kg
    beta_guess = 0.05 # Small initial decay factor
    phi_guess = 0
    c_guess = np.mean(a)
    
    initial_guesses = [A_guess, beta_guess, w_guess, phi_guess, c_guess]
    
    # Fit curve (increased maxfev for better convergence on full datasets)
    popt, pcov = curve_fit(damped, t, a, p0=initial_guesses, maxfev=10000)
    return t, a, popt, pcov

# --- Plotting and Analysis for Damped Data ---
betas, sigma_betas = [], []
omegas, sigma_omegas = [], []

# Figure 1: The main fits
fig2, axes2 = plt.subplots(2, 3, figsize=(15, 8))
axes2 = axes2.flatten()

# Figure 2: The residuals
fig_res, axes_res = plt.subplots(2, 3, figsize=(15, 8))
axes_res = axes_res.flatten()

for ax, ax_res, df, fname in zip(axes2, axes_res, dfs, filenames):
    t, a, popt, pcov = damped_fit(df)
    A, beta, w, phi, c = popt
    
    # Extract uncertainties from covariance matrix diagonals
    sigma_beta = float(np.sqrt(pcov[1, 1]))
    sigma_w = float(np.sqrt(pcov[2, 2]))
    
    betas.append(beta)
    sigma_betas.append(sigma_beta)
    omegas.append(w)
    sigma_omegas.append(sigma_w)
    
    # --- 1. Main Fit Plot ---
    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    t_smooth = np.linspace(t.min(), t.max(), 1000)
    predicted_smooth = damped(t_smooth, *popt)
    ax.plot(t_smooth, predicted_smooth, label="Damped accel fit", color="mediumblue", linewidth=2)
    
    ax.set_title(f"{fname}\nω = {w:.3f} ± {sigma_w:.4f} rad/s  |  β = {beta:.5f} ± {sigma_beta:.5f} s⁻¹", fontsize=10)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")
    
    # --- 2. Residual Plot ---
    # Residuals = Actual Data - Predicted Data
    predicted_a = damped(t, *popt)
    residuals = a - predicted_a
    
    ax_res.scatter(t, residuals, color="purple", s=10, alpha=0.7)
    ax_res.axhline(0, color="black", linestyle="--", linewidth=1.5) # Adds a baseline at y=0
    
    ax_res.set_title(f"Residuals for {fname}", fontsize=10)
    ax_res.set_xlabel("Time (s)")
    ax_res.set_ylabel("Residual Ay (m/s²)")
    ax_res.grid(True, linestyle="--", alpha=0.6)

# Finalize and save the main fits figure
fig2.subplots_adjust(hspace=0.4) 
fig2.tight_layout()
save_path_damped = os.path.join(base_dir, "2_damped_accel_fits.png")
fig2.savefig(save_path_damped, dpi=300, bbox_inches="tight")
fig_damped_res.savefig(os.path.join(base_dir, "2_damped_residuals.png"), dpi=300, bbox_inches="tight")
# Finalize and save the residuals figure
fig_res.subplots_adjust(hspace=0.4)
fig_res.tight_layout()
save_path_residuals = os.path.join(base_dir, "2_damped_residuals.png")
fig_res.savefig(save_path_residuals, dpi=300, bbox_inches="tight")

plt.show() # This will now pop up both windows!

# Calculate and print the weighted means
beta_wmean, beta_wsigma = weighted_mean(betas, sigma_betas)
w_wmean, w_wsigma = weighted_mean(omegas, sigma_omegas)

print(f"\n--- Damped Results ---")
print(f"Weighted mean beta (β): {beta_wmean:.5f} ± {beta_wsigma:.5f} s⁻¹")
print(f"Weighted mean omega (ω): {w_wmean:.5f} ± {w_wsigma:.5f} rad/s")