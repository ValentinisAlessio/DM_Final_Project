import pandas as pd

df = pd.read_csv('times/base_benchmark.csv')

df.sort_values("query", inplace = True)

print(df)