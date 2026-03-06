import os
import pandas as pd
import numpy as np

base = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(base, "3.6.csv") 
df = pd.read_csv(input_path)

#time
#df.iloc[:, 0] = df.iloc[:, 0] - 20
#acceleration
#df.iloc[:, 1] = df.iloc[:, 1] + 9.80
df.iloc[:, 1] = df.iloc[:, 1] - np.average(df.iloc[:, 1])

save_path = os.path.join(base, "3.6_cleaned.csv")
df.to_csv(save_path, index=False)