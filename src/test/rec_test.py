import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/happy')

from recommender import recommendMA
from datetime import datetime
import pandas as pd
from common import readReport

start = '2020-01-01'
end = datetime.today().strftime("%Y-%m-%d")
# end = '2020-01-18'
dates = pd.date_range(start, end).tolist()



def clearReports():
    df = pd.read_csv("./reports/rec.csv", index_col="Date")
    df.iloc[0:0].to_csv('./reports/rec.csv')
    df = pd.read_csv("./reports/trending.csv", index_col="Stock")
    df.iloc[0:0].to_csv('./reports/trending.csv')
    df = pd.read_csv("./reports/trends.csv", index_col="ID")
    df.iloc[0:0].to_csv('./reports/trends.csv')

clearReports()

for date in dates:
    recommendMA(str(date)[0:10])
