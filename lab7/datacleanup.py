import os
import pandas as pd
import numpy as np

base = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(base, "3.6.csv") 
df = pd.read_csv(input_path)

for col in df.columns:
    if "Time" not in col:
        df[col] = df[col] - np.mean(df[col])

save_path = os.path.join(base, "3.6_cleaned.csv")
df.to_csv(save_path, index=False)