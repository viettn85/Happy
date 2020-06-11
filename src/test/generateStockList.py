
import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile, readReport
csvFiles = getCsvFiles("./data/historical/")
stocks = []
values = []
for file in csvFiles:
    stocks.append(file[0:3])
    values.append(0)
pd.DataFrame.from_dict({"Stock": stocks, "Value": values}).to_csv('./data/stockList.csv', index=None)

df = pd.read_csv('./data/stockList.csv', index_col='Stock')
df.loc['BVH'].Value = 1
print(df.loc['BVH'].Value)