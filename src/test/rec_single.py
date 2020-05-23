import pandas as pd
import sys

rec = pd.read_csv('./reports/rec.csv')

stock = str(sys.argv[1])

for i in range(len(rec)):
    row = rec.iloc[i]
    buy = ""
    sell = ""
    buyMore = ""
    print(row)
    if isinstance(row.Buy,str):
        if stock in row.Buy:
            buy = stock
    if isinstance(row.BuyMore,str):
        if stock in row.BuyMore:
            buyMore =stock
    if isinstance(row.Sell,str):
        if stock in row.Sell:
            sell = stock
    row.Sell = sell
    row.Buy = buy
    row.BuyMore = buyMore
rec.to_csv('./reports/rec_single.csv')
