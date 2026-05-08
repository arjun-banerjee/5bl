import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# 1. Raw Data
# -----------------------------

aluminium_foil_0 = np.array([
    -68,-68,-68,-68,-68,-68,-75,-75,-75,-75,-75,-65,-65,-65,-65,-65,-65,
    -75,-75,-75,-75,-75,-75,-75,-75,-76,-76,-76,-76,-76,-76,-76,-76,-76
])

aluminium_foil_1 = np.array([
    -101,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,-94,
    -94,-94,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93,-93
])

aluminium_foil_2_5 = np.full(30, -105)

steel_wool_0 = np.array([
    -97,-97,-97,-97,-97,-97,-82,-82,-82,-82,-82,-82,-82,-82,-82,-82,
    -77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-77,-83,-83,-83
])

steel_wool_1 = np.array([
    -91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-91,-94,-94,-94,-94,
    -97,-97,-97,-97,-97,-78,-78,-78,-78,-78,-105,-105,-105,-97,-91
])

steel_wool_2_5 = np.array([
    -95,-95,-95,-95,-95,-95,-95,-95,-95,-95,-95,-105,-105,-105,-105,
    -105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,
    -105,-105,-105
])

ceram_wrap_0 = np.array([
    -38,-38,-38,-38,-38,-38,-38,-38,-38,-31,-31,-31,-31,-29,-29,-29,
    -29,-29,-29,-29,-29,-31,-31,-31,-31,-39,-39,-29,-29,-29,-29
])

ceram_wrap_1 = np.array([
    -105,-105,-105,-86,-86,-86,-86,-86,-86,-86,-55,-55,-54,-54,-63,
    -63,-62,-62,-55,-55,-56,-56,-56,-56,-56,-56,-61,-61,-61,-61
])

ceram_wrap_2_5 = np.array([
    -64,-64,-64,-64,-64,-64,-64,-64,-64,-62,-62,-62,-62,-62,-62,
    -62,-62,-62,-62,-62,-62,-62,-62,-62,-62,-62,-62,-62,-62,-62
])

chickenwire_0 = np.array([
    -50,-50,-50,-50,-50,-50,-50,-36,-36,-36,-36,-36,-36,-35,-35,
    -35,-35,-35,-35,-35,-35,-35,-35,-35,-35,-39,-39,-39,-39,-34
])

chickenwire_1 = np.array([
    -71,-71,-58,-58,-59,-59,-59,-59,-59,-59,-60,-60,-59,-59,-59,
    -59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-59,-56,-56,-56,-56
])

chickenwire_2_5 = np.array([
    -74,-74,-74,-74,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,
    -80,-80,-80,-80,-80,-66,-66,-66,-66,-66,-66,-66,-66,-66,-66
])

#copper_mesh_0 = np.array([
#    -105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,
#    -105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,-105,
#    -105,-105,-105,-51,-51,-51
#])

copper_mesh_0 = np.array([
    -88,-88,-88,-88,-88,-87,-87,-87,-86,-86,-85,-85,
    -86,-86,-87,-87,-88,-89,-89,-90,-91,-91,-92,-92,
    -93,-93,-94,-94,-94,-95
])

copper_mesh_1 = np.array([
    -72,-72,-72,-76,-76,-76,-76,-76,-76,-74,-74,-74,-74,-74,-74,
    -74,-74,-74,-74,-74,-74,-74,-74,-105,-105,-105,-105,-105,-105,-105
])

copper_mesh_2_5 = np.array([
    -73,-80,-80,-73,-73,-73,-73,-67,-67,-67,-67,-68,-68,-74,-74,
    -74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74,-74
])


# -----------------------------
# 2. Materials and Distances
# -----------------------------
# Ceram Wrap is removed from this list, so it is not plotted at all.

materials = [
    'aluminium_foil',
    'steel_wool',
    'copper_mesh',
    'chickenwire'
]

distances = ['0', '1', '2_5']


# -----------------------------
# 3. Control Data
# -----------------------------
# Replace these with your real control values if you have them.
# These are only used to calculate attenuation.

controls = {
    '0': np.random.normal(-25, 2, 30),
    '1': np.random.normal(-45, 3, 30),
    '2_5': np.random.normal(-65, 4, 30)
}


# -----------------------------
# 4. Uncertainties
# -----------------------------

APP_RESOLUTION_ERROR = 0.5
SPATIAL_ERROR = 1.5


# -----------------------------
# 5. Process Data
# -----------------------------

results = []

for mat in materials:
    for dist in distances:

        var_name = f"{mat}_{dist}"

        if var_name in globals():
            data = globals()[var_name]

            data = np.array(data, dtype=float)
            data = data[~np.isnan(data)]

            if len(data) > 0:

                mean_rssi = np.mean(data)

                if len(data) > 1:
                    se_mean = np.std(data, ddof=1) / np.sqrt(len(data))
                else:
                    se_mean = 0

                material_uncertainty = np.sqrt(
                    se_mean**2 +
                    APP_RESOLUTION_ERROR**2 +
                    SPATIAL_ERROR**2
                )

                control_data = controls[dist]
                mean_control = np.mean(control_data)
                se_control = np.std(control_data, ddof=1) / np.sqrt(len(control_data))

                control_uncertainty = np.sqrt(
                    se_control**2 +
                    APP_RESOLUTION_ERROR**2 +
                    SPATIAL_ERROR**2
                )

                attenuation = mean_control - mean_rssi

                attenuation_uncertainty = np.sqrt(
                    material_uncertainty**2 +
                    control_uncertainty**2
                )

                results.append({
                    'Material': mat.replace('_', ' ').title(),
                    'Distance': '2.5m' if dist == '2_5' else f'{dist}m',
                    'Mean_RSSI': mean_rssi,
                    'Control_Mean': mean_control,
                    'Attenuation_dBm': attenuation,
                    'Attenuation_Uncertainty': attenuation_uncertainty
                })


df = pd.DataFrame(results)

print(df)


# -----------------------------
# 6. Bar Chart
# Ceram Wrap removed
# -----------------------------

plt.figure(figsize=(10, 6))

bar_width = 0.15

distances_labels = sorted(
    df['Distance'].unique(),
    key=lambda x: float(x.replace('m', ''))
)

x = np.arange(len(distances_labels))

for i, mat in enumerate(df['Material'].unique()):

    mat_data = df[df['Material'] == mat]

    y = []
    yerr = []

    for d in distances_labels:
        row = mat_data[mat_data['Distance'] == d]

        if not row.empty:
            y.append(row['Attenuation_dBm'].values[0])
            yerr.append(row['Attenuation_Uncertainty'].values[0])
        else:
            y.append(0)
            yerr.append(0)

    plt.bar(
        x + i * bar_width,
        y,
        width=bar_width,
        yerr=yerr,
        capsize=5,
        label=mat
    )

plt.xlabel('Distance')
plt.ylabel('Attenuation (dBm) [Control - Measurement]')
plt.title('Bluetooth Signal Attenuation by Material and Distance')

plt.xticks(
    x + bar_width * (len(df['Material'].unique()) - 1) / 2,
    distances_labels
)

plt.legend(title='Material', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# -----------------------------
# 7. Scatter Plot
# Ceram Wrap removed
# Distances labelled
# No control/wavelength line
# -----------------------------

hole_sizes = {
    'Aluminium Foil': 1e-6,
    'Steel Wool': 3.5e-3,
    'Chickenwire': 12.7e-3,
    'Copper Mesh': 1.78e-4
}

df['Hole_Size_m'] = df['Material'].map(hole_sizes)

plt.figure(figsize=(9, 6))

for mat in df['Material'].unique():

    mat_data = df[df['Material'] == mat]

    plt.errorbar(
        mat_data['Hole_Size_m'],
        mat_data['Attenuation_dBm'],
        yerr=mat_data['Attenuation_Uncertainty'],
        fmt='o',
        label=mat,
        capsize=5,
        markersize=8
    )

    for _, row in mat_data.iterrows():
        plt.annotate(
            row['Distance'],
            xy=(row['Hole_Size_m'], row['Attenuation_dBm']),
            xytext=(6, 4),
            textcoords='offset points',
            fontsize=8
        )

plt.xscale('log')
plt.xlabel('Approximate Hole Size (m) [Log Scale]')
plt.ylabel('Attenuation (dBm)')
plt.title('Shielding Effectiveness: Attenuation vs Aperture Size')

plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()