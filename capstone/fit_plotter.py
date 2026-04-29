"""
Faraday Cage Lab — Curve Fitting Analysis
Three models fitted to RSSI vs distance for each material.

Model 1: Log-Distance Path Loss (Log-Normal Shadowing) — standard telecom model
Model 2: Power-Law Decay — empirical flexible model
Model 3: Tobit Censored MLE — corrects for -105 dBm measurement floor
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import curve_fit, minimize
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")

FLOOR = -105
D_ZERO = 0.05

aluminium_foil_0   = np.array([-68,-68,-68,-68,-68,-68,-75,-75,-75,-75,-75,-65,-65,-65,-65,-65,-65,-75,-75,-75,-75,-75,-75,-75,-75,-76,-76,-76,-76,-76,-76,-76,-76,-76])
aluminium_foil_1   = np.array([-101,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93])
aluminium_foil_2_5 = np.full(30, -105)
steel_wool_0   = np.array([-97,-97,-97,-97,-97,-97,-82,-82,-82,-82,-82,-82,-82,-82,-82,-82,-77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-83,-83,-83])
steel_wool_1   = np.array([-91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-94,-94,-94,-94,-97,-97,-97,-97,-97,-78,-78,-78,-78,-78,-105,-105,-105,-97,-91])
steel_wool_2_5 = np.array([-95,-95,-95,-95,-95,-95,-95,-95,-95,-95,-95,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105])
ceram_wrap_0   = np.array([-38,-38,-38,-38,-38,-38,-38,-38,-38,-31,-31,-31,-31,-29,-29,-29,-29,-29,-29,-29,-29,-31,-31,-31,-31,-39,-39,-29,-29,-29,-29])
ceram_wrap_1   = np.array([-105,-105,-105,-86,-86,-86,-86,-86,-86,-86,-55,-55,-54,-54,-63,-63,-62,-62,-55,-55,-56,-56,-56,-56,-56,-56,-61,-61,-61,-61])
chickenwire_0   = np.array([-50,-50,-50,-50,-50,-50,-50,-36,-36,-36,-36,-36,-36,-35,-35,-35,-35,-35,-35,-35,-35,-35,-35,-35,-35,-39,-39,-39,-39,-34])
chickenwire_1   = np.array([-71,-71,-58,-58,-59,-59,-59,-59,-59,-59,-60,-60,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-56,-56,-56,-56])
chickenwire_2_5 = np.array([-74,-74,-74,-74,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-66,-66,-66,-66,-66,-66,-66,-66,-66,-66])
copper_mesh_0   = np.array([-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-51,-51,-51])
copper_mesh_1   = np.array([-72,-72,-72,-76,-76,-76,-76,-76,-76,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-105,-105,-105,-105,-105,-105,-105])
copper_mesh_2_5 = np.array([-73,-80,-80,-73,-73,-73,-73,-67,-67,-67,-67,-68,-68,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74])

MATERIALS = {
    'Chicken Wire':   (chickenwire_0,   chickenwire_1,   chickenwire_2_5),
    'Aluminium Foil': (aluminium_foil_0, aluminium_foil_1, aluminium_foil_2_5),
    'Steel Wool':     (steel_wool_0,    steel_wool_1,    steel_wool_2_5),
    'Copper Mesh':    (copper_mesh_0,   copper_mesh_1,   copper_mesh_2_5),
    'Control':        (ceram_wrap_0,    ceram_wrap_1,    None),
}
COLORS = {
    'Control':        '#888888',
    'Aluminium Foil': '#E67E22',
    'Steel Wool':     '#2980B9',
    'Chicken Wire':   '#27AE60',
    'Copper Mesh':    '#8E44AD',
}

DIST_RAW = np.array([0.0, 1.0, 2.5])
DIST_FIT = np.array([D_ZERO, 1.0, 2.5])

def log_distance(d, A, n):
    """Log-Distance Path Loss: RSSI(d) = A - 10n·log10(d/d0), d0=1m"""
    return A - 10 * n * np.log10(np.array(d, dtype=float))

def power_law(d, A, C, k):
    """Power-Law Decay: RSSI(d) = A - C·d^k"""
    return A - C * np.power(np.array(d, dtype=float), k)

def tobit_nll(params, d_all, y_all, floor):
    """Negative log-likelihood for Tobit-censored log-distance model."""
    A, n, log_sigma = params
    sigma = np.exp(log_sigma)
    mu = A - 10 * n * np.log10(np.array(d_all, dtype=float))
    censored = y_all <= floor
    ll = np.where(censored,
                  np.log(norm.cdf(floor, mu, sigma) + 1e-300),
                  norm.logpdf(y_all, mu, sigma))
    return -np.sum(ll)

results = {}

for mat, arrs in MATERIALS.items():
    arr0, arr1, arr2 = arrs
    means = np.array([np.mean(a) if a is not None else np.nan for a in arrs])
    ses   = np.array([np.std(a, ddof=1)/np.sqrt(len(a)) if a is not None else np.nan for a in arrs])
    clip  = np.array([(np.sum(a==FLOOR)/len(a) >= 0.1) if a is not None else True for a in arrs])

    dm = DIST_FIT[~np.isnan(means)]
    rm = means[~np.isnan(means)]
    em = ses[~np.isnan(means)]

    raw_d, raw_y = [], []
    for dv, arr in zip([D_ZERO, 1.0, 2.5], arrs):
        if arr is not None:
            raw_d.extend([dv]*len(arr)); raw_y.extend(arr.tolist())
    raw_d = np.array(raw_d); raw_y = np.array(raw_y)

    r = {'means': means, 'ses': ses, 'clip': clip}

    ols_mask = ~np.isnan(means)
    dm_ols = DIST_FIT[ols_mask]
    rm_ols = means[ols_mask]
    em_ols = np.where(ses[ols_mask] == 0, 0.5, ses[ols_mask])

    try:
        if len(dm_ols) >= 2:
            p1, cov1 = curve_fit(log_distance, dm_ols, rm_ols, p0=[-70, 2],
                                 sigma=em_ols, absolute_sigma=True)
            pred1 = log_distance(dm_ols, *p1)
            ss_res = np.sum((rm_ols-pred1)**2); ss_tot = np.sum((rm_ols-np.mean(rm_ols))**2)
            r['m1'] = {'params': p1, 'cov': cov1,
                       'r2': 1-ss_res/ss_tot if ss_tot>0 else np.nan,
                       'rmse': np.sqrt(np.mean((rm_ols-pred1)**2))}
        else: r['m1'] = None
    except: r['m1'] = None

    try:
        if len(dm_ols) >= 3:
            p2, cov2 = curve_fit(power_law, dm_ols, rm_ols, p0=[-35, 25, 0.5],
                                 sigma=em_ols, absolute_sigma=True, maxfev=10000)
            pred2 = power_law(dm_ols, *p2)
            ss_res = np.sum((rm_ols-pred2)**2); ss_tot = np.sum((rm_ols-np.mean(rm_ols))**2)
            r['m2'] = {'params': p2, 'cov': cov2,
                       'r2': 1-ss_res/ss_tot if ss_tot>0 else np.nan,
                       'rmse': np.sqrt(np.mean((rm_ols-pred2)**2))}
        else: r['m2'] = None
    except: r['m2'] = None

    try:
        if len(raw_d) >= 5:
            res3 = minimize(tobit_nll, x0=[-70, 2, np.log(5)],
                            args=(raw_d, raw_y, FLOOR), method='Nelder-Mead',
                            options={'maxiter':30000,'xatol':0.001,'fatol':0.001})
            A3, n3, ls3 = res3.x
            sigma3 = np.exp(ls3)
            null_nll = tobit_nll([np.mean(raw_y[raw_y>FLOOR]) if np.any(raw_y>FLOOR) else -80,
                                  0, ls3], raw_d, raw_y, FLOOR)
            pseudo_r2 = 1 - res3.fun/null_nll if null_nll!=0 else np.nan
            pred3 = log_distance(dm, A3, n3)
            r['m3'] = {'params': (A3, n3, sigma3), 'nll': res3.fun,
                       'pseudo_r2': pseudo_r2,
                       'rmse': np.sqrt(np.mean((rm-pred3)**2)),
                       'converged': res3.success}
        else: r['m3'] = None
    except: r['m3'] = None

    results[mat] = r

print("="*75)
print("FIT RESULTS")
print("  Log-Distance: RSSI = A - 10n·log10(d)  (d0=1m)")
print("  Power-Law:    RSSI = A - C·d^k")
print("  Tobit MLE:    Log-Distance, censored at -105 dBm floor")
print("="*75)
for mat, r in results.items():
    print(f"\n{mat}")
    if r['m1']:
        A,n = r['m1']['params']
        print(f"  Log-Distance:  A={A:7.1f} dBm  n={n:.2f}   R²={r['m1']['r2']:.3f}  RMSE={r['m1']['rmse']:.2f} dB")
    if r['m2']:
        A,C,k = r['m2']['params']
        print(f"  Power-Law:     A={A:7.1f} dBm  C={C:.1f}  k={k:.2f}  R²={r['m2']['r2']:.3f}  RMSE={r['m2']['rmse']:.2f} dB")
    if r['m3']:
        A,n,sig = r['m3']['params']
        print(f"  Tobit MLE:     A={A:7.1f} dBm  n={n:.2f}  σ={sig:.1f}  McF-R²={r['m3']['pseudo_r2']:.3f}  RMSE={r['m3']['rmse']:.2f} dB")

d_smooth = np.linspace(D_ZERO, 3.0, 300)
MAT_ORDER = ['Chicken Wire', 'Aluminium Foil', 'Steel Wool', 'Copper Mesh']

MODEL_META = [
    ('m1', 'Log-Distance Path Loss',  log_distance, '#3498db'),
    ('m2', 'Power-Law Decay',         power_law,    '#e67e22'),
    ('m3', 'Tobit Censored MLE',      log_distance, '#2ecc71'),
]

fig, axes = plt.subplots(3, 4, figsize=(15, 11), sharey=True)
fig.suptitle("Faraday Cage — RSSI vs Distance: Three Model Fits",
             fontsize=13, fontweight='bold', y=0.99)

for row, (mkey, mname, mfn, mcolor) in enumerate(MODEL_META):
    for col, mat in enumerate(MAT_ORDER):
        ax = axes[row, col]
        r = results[mat]
        mat_color = COLORS[mat]
        arrs = MATERIALS[mat]

        for i, (d_raw, d_fit) in enumerate(zip(DIST_RAW, DIST_FIT)):
            arr = arrs[i]
            if arr is None: continue
            m = r['means'][i]; e = r['ses'][i]
            ax.errorbar(d_raw, m, yerr=e*2,
                        fmt='o', color=mat_color,
                        markeredgewidth=0,
                        capsize=4, capthick=1.2,
                        elinewidth=1.2, markersize=7, zorder=5)

        fr = r.get(mkey)
        if fr:
            try:
                plot_params = fr['params'][:2] if mkey == 'm3' else fr['params']
                y_fit = mfn(d_smooth, *plot_params)
                ax.plot(d_smooth, y_fit, '-', color=mcolor,
                        linewidth=2, alpha=0.85, zorder=4)

            except: pass
        else:
            ax.set_facecolor('#f0f0f0')

        ax.axhline(FLOOR, color='#c0392b', linestyle=':', linewidth=0.9, alpha=0.45)

        ax.set_xlim(-0.3, 3.1)
        ax.set_ylim(-112, -20)
        ax.grid(True, alpha=0.18, linewidth=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=8)

        if row == 0:
            ax.set_title(mat, fontsize=10, fontweight='bold', color=mat_color, pad=5)
        if col == 0:
            ax.set_ylabel("RSSI (dBm)", fontsize=9)
        if row == 2:
            ax.set_xlabel("Distance (m)", fontsize=9)
        ax.set_xticks([0, 1, 2.5])
        ax.set_xticklabels(['0','1','2.5'] if row==2 else [])

from matplotlib.lines import Line2D
legend_handles = [
    Line2D([0],[0], marker='o', color='gray', linestyle='none', markersize=7, label='Data (mean +/- 2 SE)'),
    Line2D([0],[0], color='#c0392b', linestyle=':', linewidth=1, label='-105 dBm floor'),
]
for mkey, mname, mfn, mcolor in MODEL_META:
    legend_handles.append(Line2D([0],[0], color=mcolor, linewidth=2.5, label=mname))
fig.legend(handles=legend_handles, loc='lower center', ncol=3,
           fontsize=9, frameon=True, bbox_to_anchor=(0.5, -0.03))

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("outputs/model_fits.png", dpi=150, bbox_inches='tight')
print("\nSaved model_fits.png")

fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle("Model Goodness-of-Fit Comparison", fontsize=12, fontweight='bold')

x = np.arange(len(MAT_ORDER))
width = 0.25
mcolors = ['#3498db', '#e67e22', '#2ecc71']
mlabels = ['Log-Distance', 'Power-Law', 'Tobit MLE']
mkeys   = ['m1', 'm2', 'm3']

for ax_i, (metric, ylabel, title) in enumerate([
    ('r2',   'R²  (higher = better)',          'Goodness of Fit  (R² / McFadden R²)'),
    ('rmse', 'RMSE on means (dB, lower = better)', 'Residual Error (RMSE)'),
]):
    ax = axes2[ax_i]
    for mi, (mkey, mlabel, mc) in enumerate(zip(mkeys, mlabels, mcolors)):
        vals = []
        for mat in MAT_ORDER:
            fr = results[mat].get(mkey)
            if fr is None:
                vals.append(np.nan)
            elif mkey == 'm3':
                vals.append(fr.get('pseudo_r2' if metric=='r2' else 'rmse', np.nan))
            else:
                vals.append(fr.get(metric, np.nan))

        bars = ax.bar(x + mi*width, vals, width, label=mlabel,
                      color=mc, alpha=0.82, edgecolor='white', linewidth=0.8)

    ax.set_xticks(x + width)
    ax.set_xticklabels(MAT_ORDER, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10)
    if metric == 'r2':
        ax.set_ylim(0, 1.2)
        ax.axhline(1.0, color='gray', linestyle='--', alpha=0.35, linewidth=0.8)
    else:
        ax.set_ylim(0, 55)
    ax.legend(fontsize=8.5)
    ax.grid(axis='y', alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig("outputs/model_comparison.png", dpi=150, bbox_inches='tight')
print("Saved model_comparison.png")
