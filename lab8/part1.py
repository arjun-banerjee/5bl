import pandas as pd

for file in ['1a-arjun.csv', '1a-ines.csv']:
    df = pd.read_csv(file)
    active = df[df['Voltage (V)'] > 1.5]
    H = active['Voltage (V).1'].mean() / active['Voltage (V)'].mean()
    print(f"{file} transfer ratio: {H:.4f}")

R = 1
for f in ['1b-arjun.csv', '1b-ines.csv']:
    df = pd.read_csv(f)
    on_mv = df[df['Voltage (V)'] > 1.5]['Voltage (mV)'].mean()
    off_mv = df[df['Voltage (V)'] < 0.5]['Voltage (mV)'].mean()
    corrected_v = (on_mv - off_mv) / 1000 
    current_amps = corrected_v / R
    print(f"{f} current: {current_amps * 1000:.6f} mA")