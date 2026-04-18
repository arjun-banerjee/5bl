import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter1d
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

exp1_data = pd.read_csv('12.1.csv')

time_1 = exp1_data['Time (s)'].values
bx_1 = exp1_data['Bx (µT)'].values
bz_1 = exp1_data['Bz (µT)'].values
omega_y_1 = exp1_data['ωy (rad/s)'].values
voltage_2 = exp1_data['Voltage (mV)'].values
voltage_1 = voltage_2 - np.median(voltage_2)

print(f"\n[2] Data Summary:")
print(f"    Time range: {time_1[0]:.3f} s to {time_1[-1]:.3f} s")
print(f"    Bx range: {bx_1.min():.1f} to {bx_1.max():.1f} µT")
print(f"    Bz range: {bz_1.min():.1f} to {bz_1.max():.1f} µT")
print(f"    ωy range: {omega_y_1.min():.2f} to {omega_y_1.max():.2f} rad/s")
print(f"    Voltage range: {voltage_1.min():.4f} to {voltage_1.max():.4f} mV")

skip_idx = np.where(time_1 >= 2.0)[0]
if len(skip_idx) > 0:
    start_idx = skip_idx[0]
    time_1_steady = time_1[start_idx:]
    omega_y_1_steady = omega_y_1[start_idx:]
    voltage_1_steady = voltage_1[start_idx:]
else:
    time_1_steady = time_1
    omega_y_1_steady = omega_y_1
    voltage_1_steady = voltage_1

fig, ax = plt.subplots(figsize=(10, 7))

sort_indices = np.argsort(omega_y_1_steady)
omega_sorted_all = omega_y_1_steady[sort_indices]
voltage_sorted_all = voltage_1_steady[sort_indices]

ax.plot(omega_sorted_all, voltage_sorted_all, linewidth=2.5, color='steelblue', alpha=0.8)
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax.set_xlabel('Angular Velocity ωy (rad/s)', fontsize=12)
ax.set_ylabel('High Gain Voltage (mV)', fontsize=12)
ax.set_title('Experiment 1: Parametric Plot - Voltage vs Gyroscope\n(Rotating Coil in Earth\'s Magnetic Field)', 
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Exp1_Parametric_VoltageVsOmega.png', dpi=300, bbox_inches='tight')
plt.close()

abs_omega_y = np.abs(omega_y_1_steady)
abs_voltage = np.abs(voltage_1_steady)

sort_idx = np.argsort(abs_omega_y)
omega_sorted = abs_omega_y[sort_idx]
voltage_sorted = abs_voltage[sort_idx]

mask_high_omega = abs_omega_y > 2.0
omega_filtered = abs_omega_y[mask_high_omega]
voltage_filtered = abs_voltage[mask_high_omega]

def linear_through_origin(x, m):
    return m * x

try:
    popt, pcov = curve_fit(linear_through_origin, omega_filtered, voltage_filtered, p0=[0.001])
    slope = popt[0]
    slope_err = np.sqrt(pcov[0, 0])
    print(f"\n[5] Envelope Fit Results:")
    print(f"    Slope (dV/dω): {slope:.6f} ± {slope_err:.6f} mV·s/rad")
    
    coeffs = np.polyfit(omega_filtered, voltage_filtered, 1)
    print(f"    Linear fit (with intercept): V = {coeffs[0]:.6f}·ω + {coeffs[1]:.6f}")
    
    omega_fit = np.linspace(0, omega_filtered.max(), 100)
    voltage_fit = linear_through_origin(omega_fit, slope)
except Exception as e:
    print(f"    Error in fitting: {e}")
    slope = None

fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(omega_sorted, voltage_sorted, linewidth=2.5, color='steelblue', alpha=0.7, label='Envelope data')

if slope is not None:
    omega_fit = np.linspace(0, omega_sorted.max(), 100)
    voltage_fit_line = slope * omega_fit
    ax.plot(omega_fit, voltage_fit_line, 'r-', linewidth=2.5, label=f'Fit: V = {slope:.5f}·ω')

ax.set_xlabel('|Angular Velocity| (rad/s)', fontsize=12)
ax.set_ylabel('|Voltage| (mV)', fontsize=12)
ax.set_title('Experiment 1: Envelope Analysis\nLinear Fit to Extract Magnetic Field', 
             fontsize=13, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Exp1_Envelope_Fit.png', dpi=300, bbox_inches='tight')
plt.close()

N_coils_1 = 6
a_coil_1 = 0.00975 
if slope is not None:
    B_h_from_slope = (slope * 1e-3) / (N_coils_1 * a_coil_1) 
    B_h_nT = B_h_from_slope * 1e9  
    print(f"\n[6] Calculated Earth's Magnetic Field Component:")
    print(f"    B_horizontal = {B_h_from_slope:.2e} T = {B_h_nT:.1f} nT")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.plot(time_1_steady, voltage_1_steady, linewidth=1, color='steelblue', label='Voltage (mV)')
ax1.set_ylabel('Voltage (mV)', fontsize=11)
ax1.set_title('Experiment 1: Time-Domain Data', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')

ax2.plot(time_1_steady, omega_y_1_steady, linewidth=1, color='darkred', label='Angular Velocity ωy (rad/s)')
ax2.set_xlabel('Time (s)', fontsize=11)
ax2.set_ylabel('ωy (rad/s)', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.close()