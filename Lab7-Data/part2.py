import os 
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def retrieve(files):
    base = os.path.dirname(os.path.abspath(__file__))
    return [pd.read_csv(os.path.join(base, f)) for f in files]

def undamped(t,A,w,phi,c):
    return A*np.cos(w*t+phi)+c

def fit_undamped(df):
    t = df["Time (s)"].values
    a = df["Ay (m/s²)"].values
    F = df["Fᵧ (N)"].values
    initial_guesses = [np.ptp(a)/2,2*np.pi/0.86,0,np.mean(a)]
    popt,pcov = curve_fit(undamped,t,a,p0=initial_guesses)
    return popt,pcov

def k_undamped(popt,m):
    return m*popt[1]**2

def avg_k(dfs):
    ks = []
    for df in dfs:
        popt, _ = fit_undamped(df)
        ks.append(k_undamped(popt,0.2305))
    return np.mean(ks), np.std(ks), ks

df2s = retrieve(["2.1.csv", "2.2.csv", "2.3.csv", "2.4.csv", "2.5.csv", "2.6.csv"])


df2s = retrieve(["2.1.csv", "2.2.csv", "2.3.csv", "2.4.csv", "2.5.csv", "2.6.csv"])
filenames = ["2.1.csv", "2.2.csv", "2.3.csv", "2.4.csv", "2.5.csv", "2.6.csv"]

# 1. Create a 2x3 grid of subplots. 
# figsize=(15, 8) makes it wide enough so the plots don't get squished.
fig, axes = plt.subplots(2, 3, figsize=(15, 8))

# Flatten the 2x3 grid into a 1D list so we can easily loop through it
axes = axes.flatten() 

for i in range(len(df2s)):
    df = df2s[i]
    ax = axes[i]
    fname = filenames[i]
    
    # Extract the data for plotting
    t = df["Time (s)"].values
    a = df["Ay (m/s²)"].values
    
    # Get the fit parameters and calculate k
    popt, _ = fit_undamped(df)
    k = k_undamped(popt, 0.2305)
    
    # Plot the raw scatter data
    ax.scatter(t, a, label="Raw Data", color="gray", s=10, alpha=0.7)
    
    # Plot the fitted curve
    # We create a "dense" time array with 500 points so the sine wave plots smoothly 
    # rather than looking jagged between your actual data points.
    t_smooth = np.linspace(min(t), max(t), 500)
    ax.plot(t_smooth, undamped(t_smooth, *popt), label="Fitted Curve", color="red", linewidth=2)
    
    # Format the subplot
    ax.set_title(f"{fname} | Calculated k = {k:.2f} N/m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Ay (m/s²)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

# 2. Automatically adjust spacing so titles and axis labels don't overlap
plt.tight_layout()

# 3. Display the masterpiece
plt.show()

# (Optional) You can still print your overall averages!
avg_k2, std_k2, all_k2s = avg_k(df2s)
print(f"\nOverall Average k: {avg_k2:.3f} ± {std_k2:.3f} N/m")