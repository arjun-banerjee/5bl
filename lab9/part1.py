import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

freq_hz = np.array([50, 100, 300, 700, 2500, 5000, 10000])
v_0 = np.array([2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])
v_c = np.array([1.9, 1.7, 0.90, 0.45, 0.13, 0.06, 0.03])
phi_deg = np.array([-5, -32, -55, -81, -90, -86, -86]) 

omega = 2 * np.pi * freq_hz
gain = v_c / v_0

plt.figure(figsize=(10, 6))
plt.loglog(omega, gain, 'ro-', markersize=8, linewidth=2, label='Measured $V_C/V_0$')
plt.title('Low-Pass RC Filter: Gain vs. Angular Frequency', fontsize=14)
plt.xlabel('Angular Frequency $\omega$ (rad/s)', fontsize=12)
plt.ylabel('Voltage Ratio $V_C/V_0$ (Gain)', fontsize=12)
plt.grid(True, which="both", linestyle="--", alpha=0.7)
plt.legend()
plt.show()

def low_pass_model(w, A, tau):
    return A / np.sqrt(1 + (w**2 * tau**2))

popt, pcov = curve_fit(low_pass_model, omega, gain, p0=[1.0, 0.001])
A_fit, tau_fit = popt
A_err, tau_err = np.sqrt(np.diag(pcov))

print(f"Fit Results (Amp):")
print(f"A = {A_fit:.4f} ± {A_err:.4f}")
print(f"τ = {tau_fit:.6e} s ± {tau_err:.6e} s")

w_smooth = np.logspace(np.log10(omega.min()), np.log10(omega.max()), 200)
plt.figure(figsize=(10, 6))
plt.loglog(omega, gain, 'ro', label='Experimental Data')
plt.loglog(w_smooth, low_pass_model(w_smooth, *popt), 'b-', 
           label=f'Fit: A={A_fit:.2f}, τ={tau_fit*1e3:.2f}ms')
plt.title('Low-Pass RC Filter: Amplitude Fit')
plt.xlabel('Angular Frequency ω (rad/s)')
plt.ylabel('$V_C/V_0$')
plt.grid(True, which="both", ls="--", alpha=0.6)
plt.legend()
plt.show()

def phase_model(w, tau):
    return -np.degrees(np.arctan(w * tau))

popt_p, pcov_p = curve_fit(phase_model, omega, phi_deg, p0=[0.001])
tau_phi = popt_p[0]
tau_phi_err = np.sqrt(np.diag(pcov_p))[0]

print(f"Calculated tau (from phase): {tau_phi:.6e} ± {tau_phi_err:.6e} s")

w_smooth_p = np.logspace(np.log10(omega.min()), np.log10(omega.max()), 250)
plt.figure(figsize=(10, 6))
plt.semilogx(omega, phi_deg, 'ro', label='Measured $\phi_C$')
plt.semilogx(w_smooth_p, phase_model(w_smooth_p, tau_phi), 'b-', 
             label=f'Theoretical: $\\tau$ = {tau_phi*1e3:.3f} ± {tau_phi_err*1e3:.3f} ms')
plt.title('Phase Shift vs. Angular Frequency (Low-Pass RC Filter)', fontsize=14)
plt.xlabel('Angular Frequency $\omega$ (rad/s)', fontsize=12)
plt.ylabel('Phase Shift $\phi_C$ (Degrees)', fontsize=12)
plt.grid(True, which="both", ls="--", alpha=0.6)
plt.legend()
plt.show()