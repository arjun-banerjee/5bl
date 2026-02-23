import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FY_COL = "Fᵧ (N)"
RY_COL = "rᵧ (m)"

def fit_spring_constant(df):
    """Fit Fᵧ = -k·rᵧ (through origin). Returns k, fy, ry (filtered)."""
    fy = df[FY_COL].values
    ry = df[RY_COL].values
    mask = np.abs(ry) > 1e-6
    if mask.sum() < 2:
        return np.nan, np.array([]), np.array([])
    fy, ry = fy[mask], ry[mask]
    k = -np.dot(fy, ry) / np.dot(ry, ry)
    return k, fy, ry

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dfs = []
    for fname in ["1.1.csv", "1.2.csv", "1.3.csv"]:
        df = pd.read_csv(os.path.join(script_dir, fname))
        dfs.append(df[df["Time (s)"] <= 10])
    df = pd.concat(dfs, ignore_index=True)
    k, fy, ry = fit_spring_constant(df)
    
    print(k)

    fig, ax = plt.subplots()
    ax.scatter(ry, fy, s=4, alpha=0.5, c="steelblue", label="Data")
    r_fit = np.linspace(ry.min(), ry.max(), 100)
    ax.plot(r_fit, -k * r_fit, "r-", lw=2, label=f"Fᵧ = -{k:.2f}rᵧ")
    ax.set_xlabel("rᵧ (m)")
    ax.set_ylabel("Fᵧ (N)")
    ax.set_title("Hooke's law: Fᵧ = -k·rᵧ")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, "exp1_fit.png"), dpi=150)
    plt.show()

if __name__ == "__main__":
    main()
