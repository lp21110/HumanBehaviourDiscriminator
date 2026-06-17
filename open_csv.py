import pandas as pd
from pathlib import Path

csv_path = Path(__file__).with_name("EPIC_100_validation_dataset.csv")
#example_df_1 = pd.read_csv(csv_path)

#(example_df_1.head())

#headers = example_df_1.columns.tolist()

df = pd.read_csv(csv_path, usecols=['start_timestamp', 'stop_timestamp', 'narration'])

print (df)