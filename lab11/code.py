import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore') # student doesn't want to see warnings

g = 9.80
mu_th = 13 / 1000 / 2.962 
print(f"Theory mu: {mu_th:.6f}")

#exp1
n1 = np.array([1, 2, 3, 4, 5, 6])
f_min, f_max = np.array([8.09, 15.7, 23.6, 33.6, 40.95, 48.32]), np.array([8.11, 16.0, 23.7, 34.1, 41.05, 48.39])
f1, df1 = (f_min + f_max) / 2, (f_max - f_min) / 2
T1, L1 = 0.150 * g, 0.935

p1, pc1 = curve_fit(lambda x, a: a*x, n1, f1, sigma=df1, absolute_sigma=True)
s1 = p1[0]
mu1 = T1 / (4 * L1**2 * s1**2)
print(f"Exp1 mu: {mu1:.6f}")

res1 = f1 - s1*n1
norm_res1 = res1 / df1

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.errorbar(n1, f1, yerr=df1, fmt='o', capsize=5, label='data'); ax1.plot(n1, s1*n1, 'r-', label=f'fit f={s1:.2f}n')
ax1.set_title("Exp 1: Freq vs n"); ax1.set_ylabel("Freq (Hz)"); ax1.set_xlabel("n"); ax1.legend()

psize1 = 50 + 200 * (df1 / df1.max())
for i in range(len(n1)):
    # scatter for variable size cross
    ax2.scatter(n1[i], norm_res1[i], s=psize1[i], marker='x', color='blue', alpha=0.7)
    # errorbar for the +/- 1 sigma bar
    ax2.errorbar(n1[i], norm_res1[i], yerr=1.0, fmt='none', ecolor='blue', capsize=5, alpha=0.5)
ax2.axhline(0, color='r', ls='--'); ax2.fill_between([0, 7], -1, 1, alpha=0.1, color='g')
ax2.set_title("Normalized Residuals (Exp 1)"); ax2.set_ylabel("sigma"); ax2.set_xlabel("n")
plt.tight_layout(); plt.savefig('exp1_analysis.png'); plt.show()

#exp1
n2 = np.array([2, 3, 4, 5, 6, 7])
m2 = np.array([397, 235, 160, 95, 65, 30]) / 1000
T2, dT2 = m2 * g, m2 * 0.01 
f2, L2 = 30, 1.21

p2, _ = curve_fit(lambda n, A: A/n**2, n2, T2, sigma=dT2, absolute_sigma=True)
A2 = p2[0]
mu2 = A2 / ((2*L2*f2)**2)
print(f"Exp2 mu: {mu2:.6f}")

fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5))
ax3.errorbar(n2, T2, yerr=dT2, fmt='go', capsize=5); ax3.plot(np.linspace(1.5, 7.5, 100), A2/np.linspace(1.5, 7.5, 100)**2, 'r-')
ax3.set_title("Exp 2: Tension vs n"); ax3.set_ylabel("Tension (N)"); ax3.set_xlabel("n")
ax4.errorbar(n2, T2 * n2**2, yerr=dT2 * n2**2, fmt='go', capsize=5); ax4.axhline(A2, color='r', label=f'A={A2:.3f}')
ax4.set_title("Linearized: T*n^2 vs n"); ax4.set_ylabel("T*n^2"); ax4.set_xlabel("n"); ax4.legend()
plt.tight_layout(); plt.savefig('exp2_analysis.png'); plt.show()


# exp3
n3 = np.arange(1, 8)
L_a = np.array([21.0, 40.5, 60.3, 79.5, 98.2, 117.7, 137.4]) / 100
L_b = np.array([21.5, 40.0, 60.3, 80.0, 98.5, 117.8, 137.0]) / 100
L3, dL3 = (L_a + L_b) / 2, np.maximum(np.abs(L_a - L_b)/2, 0.001)

p3, _ = curve_fit(lambda x, a: a*x, n3, L3, sigma=dL3, absolute_sigma=True)
s3 = p3[0]
mu3 = (0.1*g) / (4 * 40**2 * s3**2)
print(f"Exp3 mu: {mu3:.6f}")

norm_res3 = (L3 - s3*n3) / dL3

fig, (ax5, ax6) = plt.subplots(1, 2, figsize=(12, 5))
ax5.errorbar(n3, L3*100, yerr=dL3*100, fmt='o', color='purple', capsize=5); ax5.plot(n3, s3*n3*100, 'r-')
ax5.set_title("Exp 3: Length vs n"); ax5.set_ylabel("Length (cm)"); ax5.set_xlabel("n")

psize3 = 50 + 150 * (dL3 / dL3.max())
for i in range(len(n3)):
    ax6.scatter(n3[i], norm_res3[i], s=psize3[i], marker='x', color='purple', alpha=0.7)
    ax6.errorbar(n3[i], norm_res3[i], yerr=1.0, fmt='none', ecolor='purple', capsize=5, alpha=0.5)
ax6.axhline(0, color='r', ls='--'); ax6.fill_between([0, 8], -1, 1, alpha=0.1, color='g')
ax6.set_title("Normalized Residuals (Exp 3)"); ax6.set_ylabel("sigma"); ax6.set_xlabel("n")
plt.tight_layout(); plt.savefig('exp3_analysis.png'); plt.show()
