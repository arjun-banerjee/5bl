import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import chi2
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
fig_dpi = 150
import os
os.makedirs('plots', exist_ok=True)

g = 9.80  
g_unc = 0.01  

print("EXPERIMENT 1: Fixed Length and Tension, Varying Frequency")

n_exp1 = np.array([1, 2, 3, 4, 5, 6])
f_min_exp1 = np.array([8.09, 15.7, 23.6, 33.6, 40.95, 48.32])
f_max_exp1 = np.array([8.11, 16.0, 23.7, 34.1, 41.05, 48.39])

f_center_exp1 = (f_min_exp1 + f_max_exp1) / 2
f_unc_exp1 = (f_max_exp1 - f_min_exp1) / 2

print("\nExperiment 1 Setup:")
print("String mass: 13 g")
print("Total string length: 2.962 m")
print("Mass per unit length (theoretical): 0.00439 kg/m")
print("Hanging mass: 150 g")
print("Length in tension (L): 93.5 cm = 0.935 m")

m_hang_1 = 0.150  
T_exp1 = m_hang_1 * g
T_exp1_unc = m_hang_1 * g_unc

print(f"Tension T = {T_exp1:.4f} ± {T_exp1_unc:.5f} N")

mu_th_exp1 = 13 / 1000 / 2.962  
print(f"Theoretical μ = {mu_th_exp1:.6f} kg/m")

print("\nFrequency Data:")
print("n | f_min (Hz) | f_max (Hz) | f_center (Hz) | Δf (Hz)")
for i in range(len(n_exp1)):
    print(f"{n_exp1[i]} | {f_min_exp1[i]:.2f} | {f_max_exp1[i]:.2f} | {f_center_exp1[i]:.3f} | {f_unc_exp1[i]:.3f}")

popt1, pcov1 = curve_fit(lambda x, a: a*x, n_exp1, f_center_exp1, 
                          sigma=f_unc_exp1, absolute_sigma=True)
a_fit1 = popt1[0]
a_unc1 = np.sqrt(pcov1[0, 0])

print(f"\nFit Results: f = {a_fit1:.4f} * n")
print(f"Slope = {a_fit1:.6f} ± {a_unc1:.6f} Hz")

L_exp1 = 0.935  
mu_exp1 = T_exp1 / (4 * L_exp1**2 * a_fit1**2)

d_mu_dslope = -2 * T_exp1 / (4 * L_exp1**2 * a_fit1**3)
mu_unc1 = abs(d_mu_dslope) * a_unc1

print(f"\nMeasured μ = {mu_exp1:.6f} ± {mu_unc1:.6f} kg/m")
print(f"Theoretical μ = {mu_th_exp1:.6f} kg/m")

diff1 = abs(mu_exp1 - mu_th_exp1)
sigma_diff1 = np.sqrt(mu_unc1**2)
z_score1 = diff1 / sigma_diff1
print(f"Difference: {diff1:.6f} kg/m")
print(f"Z-score: {z_score1:.2f} (agreement within {z_score1:.1f}σ)")

f_fitted1 = a_fit1 * n_exp1
residuals1 = f_center_exp1 - f_fitted1
normalized_residuals1 = residuals1 / f_unc_exp1
chi2_stat1 = np.sum(((f_center_exp1 - f_fitted1) / f_unc_exp1)**2)
dof1 = len(n_exp1) - 1  
chi2_red1 = chi2_stat1 / dof1

print(f"\nChi-squared Analysis:")
print(f"χ² = {chi2_stat1:.4f}")
print(f"DOF = {dof1}")
print(f"Reduced χ² = {chi2_red1:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].errorbar(n_exp1, f_center_exp1, yerr=f_unc_exp1, fmt='o', 
                 markersize=6, capsize=4, color='black', ecolor='black')
n_fit = np.linspace(0, 8, 100)
axes[0].plot(n_fit, a_fit1 * n_fit, 'k-', linewidth=1.5)
axes[0].set_xlabel('Harmonic number (n)', fontsize=10)
axes[0].set_ylabel('Frequency (Hz)', fontsize=10)
axes[0].set_title('Experiment 1: Frequency vs Harmonic Number', fontsize=11)
axes[0].grid(True, alpha=0.3)

ax_residuals = axes[1]
ax_residuals.errorbar(n_exp1, normalized_residuals1, yerr=1.0, 
                     fmt='o', markersize=6, capsize=4, color='black', ecolor='black')
ax_residuals.axhline(y=0, color='k', linestyle='--', linewidth=1)
ax_residuals.axhline(y=1, color='gray', linestyle=':', linewidth=0.8)
ax_residuals.axhline(y=-1, color='gray', linestyle=':', linewidth=0.8)
ax_residuals.set_xlabel('Harmonic number (n)', fontsize=10)
ax_residuals.set_ylabel('Normalized Residuals (σ)', fontsize=10)
ax_residuals.set_title('Normalized Residuals', fontsize=11)
ax_residuals.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/exp1_analysis.png', dpi=fig_dpi, bbox_inches='tight')
print("\nSaved: plots/exp1_analysis.png")
plt.close()

print("EXPERIMENT 2: Fixed Length and Frequency, Varying Tension")

n_exp2 = np.array([2, 3, 4, 5, 6, 7])
m_measured_exp2 = np.array([397, 235, 160, 95, 65, 30])  
f_exp2 = 30  
L_exp2 = 1.21  
L_exp2_unc = 0.01 

print("\nExperiment 2 Setup:")
print(f"Fixed frequency: {f_exp2} Hz")
print(f"String length L: {L_exp2} m")
print(f"String mass: 13 g, total length: 2.962 m")
print(f"Theoretical μ: {mu_th_exp1:.6f} kg/m")

m_measured_exp2_kg = m_measured_exp2 / 1000

T_exp2 = m_measured_exp2_kg * g
T_exp2_unc = m_measured_exp2_kg * g_unc

print("\nMass and Tension Data:")
print("n | Mass (g) | Tension (N) | ΔT (N)")
for i in range(len(n_exp2)):
    print(f"{n_exp2[i]} | {m_measured_exp2[i]:.1f} | {T_exp2[i]:.4f} | {T_exp2_unc[i]:.6f}")

def T_model(n, A):
    return A / (n**2)

popt2, pcov2 = curve_fit(T_model, n_exp2, T_exp2, sigma=T_exp2_unc, absolute_sigma=True)
A_fit2 = popt2[0]
A_unc2 = np.sqrt(pcov2[0, 0])

mu_exp2 = A_fit2 / ((2 * L_exp2 * f_exp2)**2)
d_mu_dA = 1 / ((2 * L_exp2 * f_exp2)**2)
mu_unc2 = abs(d_mu_dA) * A_unc2

print(f"\nFit Results: T = {A_fit2:.4f} / n²")
print(f"A = {A_fit2:.6f} ± {A_unc2:.6f}")

print(f"\nMeasured μ = {mu_exp2:.6f} ± {mu_unc2:.6f} kg/m")
print(f"Theoretical μ = {mu_th_exp1:.6f} kg/m")
print(f"From Exp 1: μ = {mu_exp1:.6f} ± {mu_unc1:.6f} kg/m")

diff2_theory = abs(mu_exp2 - mu_th_exp1)
sigma_diff2_theory = np.sqrt(mu_unc2**2)
z_score2_theory = diff2_theory / sigma_diff2_theory
print(f"\nComparison to theoretical:")
print(f"Difference: {diff2_theory:.6f} kg/m")
print(f"Z-score: {z_score2_theory:.2f} (agreement within {z_score2_theory:.1f}σ)")

diff2_exp1 = abs(mu_exp2 - mu_exp1)
sigma_diff2_exp1 = np.sqrt(mu_unc2**2 + mu_unc1**2)
z_score2_exp1 = diff2_exp1 / sigma_diff2_exp1
print(f"\nComparison to Exp 1:")
print(f"Difference: {diff2_exp1:.6f} kg/m")
print(f"Z-score: {z_score2_exp1:.2f} (agreement within {z_score2_exp1:.1f}σ)")

T_fitted2 = T_model(n_exp2, A_fit2)
residuals2 = T_exp2 - T_fitted2
normalized_residuals2 = residuals2 / T_exp2_unc
chi2_stat2 = np.sum(((T_exp2 - T_fitted2) / T_exp2_unc)**2)
dof2 = len(n_exp2) - 1

print(f"\nChi-squared Analysis:")
print(f"χ² = {chi2_stat2:.4f}")
print(f"DOF = {dof2}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].errorbar(n_exp2, T_exp2, yerr=T_exp2_unc, fmt='o', 
                 markersize=6, capsize=4, color='black', ecolor='black')
n_fit2 = np.linspace(1.5, 7.5, 100)
axes[0].plot(n_fit2, T_model(n_fit2, A_fit2), 'k-', linewidth=1.5)
axes[0].set_xlabel('Harmonic number (n)', fontsize=10)
axes[0].set_ylabel('Tension (N)', fontsize=10)
axes[0].set_title('Experiment 2: Tension vs Harmonic Number', fontsize=11)
axes[0].grid(True, alpha=0.3)

axes[1].errorbar(n_exp2, T_exp2 * n_exp2**2, 
                 yerr=T_exp2_unc * n_exp2**2, fmt='o', 
                 markersize=6, capsize=4, color='black', ecolor='black')
axes[1].axhline(y=A_fit2, color='k', linestyle='-', linewidth=1.5)
axes[1].set_xlabel('Harmonic number (n)', fontsize=10)
axes[1].set_ylabel('T·n² (N)', fontsize=10)
axes[1].set_title('Linearized Fit: T·n² vs n', fontsize=11)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/exp2_analysis.png', dpi=fig_dpi, bbox_inches='tight')
print("\nSaved: plots/exp2_analysis.png")
plt.close()

print("EXPERIMENT 3: Fixed Tension and Frequency, Varying Length")

n_exp3 = np.array([1, 2, 3, 4, 5, 6, 7])
L_trial1_exp3 = np.array([21.0, 40.5, 60.3, 79.5, 98.2, 117.7, 137.4])  
L_trial2_exp3 = np.array([21.5, 40.0, 60.3, 80.0, 98.5, 117.8, 137.0])  

L_trial1_exp3 = L_trial1_exp3 / 100
L_trial2_exp3 = L_trial2_exp3 / 100
L_avg_exp3 = (L_trial1_exp3 + L_trial2_exp3) / 2
L_unc_exp3 = np.abs(L_trial1_exp3 - L_trial2_exp3) / 2

print("\nExperiment 3 Setup:")
print("Fixed frequency: 40 Hz")
print("Fixed hanging mass: 0.1 kg")
m_hang_3 = 0.1  
T_exp3 = m_hang_3 * g
print(f"Tension T = {T_exp3:.4f} N")
f_exp3 = 40  
print(f"Theoretical μ: {mu_th_exp1:.6f} kg/m")

print("\nLength Data:")
print("n | L_trial1 (cm) | L_trial2 (cm) | L_avg (cm) | ΔL (cm)")
for i in range(len(n_exp3)):
    print(f"{n_exp3[i]} | {L_trial1_exp3[i]*100:.1f} | {L_trial2_exp3[i]*100:.1f} | {L_avg_exp3[i]*100:.2f} | {L_unc_exp3[i]*100:.2f}")

L_unc_exp3_adj = np.where(L_unc_exp3 < 0.001, 0.001, L_unc_exp3)

popt3, pcov3 = curve_fit(lambda x, a: a*x, n_exp3, L_avg_exp3, 
                          sigma=L_unc_exp3_adj, absolute_sigma=True, maxfev=2000)
c_fit3 = popt3[0]
c_unc3 = np.sqrt(pcov3[0, 0])

print(f"\nFit Results: L = {c_fit3:.6f} * n")
print(f"Slope = {c_fit3:.6f} ± {c_unc3:.6f} m")

mu_exp3 = T_exp3 / (4 * f_exp3**2 * c_fit3**2)

d_mu_dc = -2 * T_exp3 / (4 * f_exp3**2 * c_fit3**3)
mu_unc3 = abs(d_mu_dc) * c_unc3

if not np.isfinite(mu_unc3):
    mu_unc3 = mu_exp3 * 0.01  

print(f"\nMeasured μ = {mu_exp3:.6f} ± {mu_unc3:.6f} kg/m")
print(f"Theoretical μ = {mu_th_exp1:.6f} kg/m")
print(f"From Exp 1: μ = {mu_exp1:.6f} ± {mu_unc1:.6f} kg/m")
print(f"From Exp 2: μ = {mu_exp2:.6f} ± {mu_unc2:.6f} kg/m")

diff3 = abs(mu_exp3 - mu_th_exp1)
sigma_diff3 = np.sqrt(mu_unc3**2)
z_score3 = diff3 / sigma_diff3
print(f"\nComparison to theoretical:")
print(f"Difference: {diff3:.6f} kg/m")
print(f"Z-score: {z_score3:.2f} (agreement within {z_score3:.1f}σ)")

L_fitted3 = c_fit3 * n_exp3
residuals3 = L_avg_exp3 - L_fitted3
normalized_residuals3 = residuals3 / L_unc_exp3_adj
chi2_stat3 = np.sum(((L_avg_exp3 - L_fitted3) / L_unc_exp3_adj)**2)
dof3 = len(n_exp3) - 1
chi2_red3 = chi2_stat3 / dof3

print(f"\nChi-squared Analysis:")
print(f"χ² = {chi2_stat3:.4f}")
print(f"DOF = {dof3}")
print(f"Reduced χ² = {chi2_red3:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].errorbar(n_exp3, L_avg_exp3*100, yerr=L_unc_exp3*100, fmt='o', 
                 markersize=6, capsize=4, color='black', ecolor='black')
n_fit3 = np.linspace(0, 8, 100)
axes[0].plot(n_fit3, c_fit3 * n_fit3 * 100, 'k-', linewidth=1.5)
axes[0].set_xlabel('Harmonic number (n)', fontsize=10)
axes[0].set_ylabel('Length (cm)', fontsize=10)
axes[0].set_title('Experiment 3: Length vs Harmonic Number', fontsize=11)
axes[0].grid(True, alpha=0.3)

ax_residuals = axes[1]
ax_residuals.errorbar(n_exp3, normalized_residuals3, yerr=1.0, 
                     fmt='o', markersize=6, capsize=4, color='black', ecolor='black')
ax_residuals.axhline(y=0, color='k', linestyle='--', linewidth=1)
ax_residuals.axhline(y=1, color='gray', linestyle=':', linewidth=0.8)
ax_residuals.axhline(y=-1, color='gray', linestyle=':', linewidth=0.8)
ax_residuals.set_xlabel('Harmonic number (n)', fontsize=10)
ax_residuals.set_ylabel('Normalized Residuals (σ)', fontsize=10)
ax_residuals.set_title('Normalized Residuals', fontsize=11)
ax_residuals.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/exp3_analysis.png', dpi=fig_dpi, bbox_inches='tight')
print("\nSaved: plots/exp3_analysis.png")
plt.close()

print("SUMMARY: COMPARISON OF ALL MEASUREMENTS")

print(f"\nTheoretical linear mass density: {mu_th_exp1:.6f} kg/m")
print(f"\nExperiment 1 (f vs n): {mu_exp1:.6f} ± {mu_unc1:.6f} kg/m (χ²_red = {chi2_red1:.3f})")
print(f"Experiment 2 (T vs n): {mu_exp2:.6f} ± {mu_unc2:.6f} kg/m")
print(f"Experiment 3 (L vs n): {mu_exp3:.6f} ± {mu_unc3:.6f} kg/m (χ²_red = {chi2_red3:.3f})")

mu_all = np.array([mu_exp1, mu_exp2, mu_exp3])
mu_unc_all = np.array([mu_unc1, mu_unc2, mu_unc3])
mu_avg = np.average(mu_all, weights=1/mu_unc_all**2)
mu_avg_unc = 1 / np.sqrt(np.sum(1/mu_unc_all**2))

print(f"\nWeighted average: {mu_avg:.6f} ± {mu_avg_unc:.6f} kg/m")

diff_avg = abs(mu_avg - mu_th_exp1)
z_score_avg = diff_avg / mu_avg_unc
print(f"Difference from theory: {diff_avg:.6f} kg/m ({z_score_avg:.2f}σ)")