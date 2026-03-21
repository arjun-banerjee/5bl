import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

freq = np.array([500, 1000, 5000, 10000, 50000])
V0 = np.array([2.0, 2.0, 2.0, 2.0, 2.0])
VL = np.array([0.550, 0.998, 1.9, 2.0, 2.0])
phase_deg = np.array([64.5, 56.1, 18.0, 3.6, 0.0])

omega = 2 * np.pi * freq
ratio = VL / V0


def model(w, A, tau):
    return A * (w * tau) / np.sqrt(1 + (w * tau)**2)

popt, pcov = curve_fit(model, omega, ratio, p0=[1.0, 1.0/(2*np.pi*1000)])
A_fit, tau_fit = popt
A_err, tau_err = np.sqrt(np.diag(pcov))

print(f"A = {A_fit:.4f} +/- {A_err:.4f}")
print(f"tau = {tau_fit:.6f} +/- {tau_err:.6f} s")
print(f"f_c = {1/(2*np.pi*tau_fit):.1f} Hz")


def plot_amplitude():
    omega_fit = np.logspace(np.log10(omega.min()*0.4), np.log10(omega.max()*2), 500)
    ratio_fit = model(omega_fit, *popt)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(omega, ratio, 'o', color='black', markersize=6, label='Data', zorder=3)
    ax.loglog(omega_fit, ratio_fit, '-', color='steelblue', linewidth=1.8,
              label=rf'Fit: $A={A_fit:.3f} \pm {A_err:.4f}$, $\tau={tau_fit*1e3:.3f} \pm {tau_err*1e3:.4f}$ ms')
    ax.set_xlabel(r'$\omega$ (rad s$^{-1}$)', fontsize=12)
    ax.set_ylabel(r'$V_L / V_0$', fontsize=12)
    ax.set_title(r'Log-log plot of amplitude ratio $V_L/V_0$ vs angular frequency', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/part2_amplitude_plot.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_phase():
    omega_fit = np.logspace(np.log10(omega.min()*0.4), np.log10(omega.max()*2), 500)
    phase_theory = np.degrees(np.arctan(1.0 / (omega_fit * tau_fit)))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogx(omega, phase_deg, 'o', color='black', markersize=6, label='Data', zorder=3)
    ax.semilogx(omega_fit, phase_theory, '-', color='tomato', linewidth=1.8,
                label=rf'Theory ($\tau = {tau_fit*1e3:.3f}$ ms)')
    ax.set_xlabel(r'$\omega$ (rad s$^{-1}$)', fontsize=12)
    ax.set_ylabel(r'Phase shift $\phi_L$ (degrees)', fontsize=12)
    ax.set_title(r'Semi-log plot of phase shift $\phi_L$ vs angular frequency', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/part2_phase_plot.png', dpi=150, bbox_inches='tight')
    plt.show()


plot_amplitude()
plot_phase()
