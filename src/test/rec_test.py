import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/happy')

from recommender import recommendMA, recommendYellowRedBlue2
from datetime import datetime
import pandas as pd
from common import readReport, readFile

start = '2020-01-01'
# start = '2019-07-26'
end = datetime.today().strftime("%Y-%m-%d")
# end = '2020-03-'
dates = pd.date_range(start, end).tolist()



def testMARecommendation():
    df = pd.read_csv("./reports/rec.csv", index_col="Date")
    df.iloc[0:0].to_csv('./reports/rec.csv')
    df = pd.read_csv("./reports/trending.csv", index_col="Stock")
    df.iloc[0:0].to_csv('./reports/trending.csv')
    df = pd.read_csv("./reports/trends.csv", index_col="ID")
    df.iloc[0:0].to_csv('./reports/trends.csv')
    for date in dates:
        recommendMA(str(date)[0:10])

def testYRBRecommendation():
    df = pd.read_csv("./reports/yrb_rec.csv", index_col="Date")
    df.iloc[0:0].to_csv('./reports/yrb_rec.csv')
    df = pd.read_csv("./reports/yrb_trending.csv", index_col="Stock")
    df.iloc[0:0].to_csv('./reports/yrb_trending.csv')
    df = pd.read_csv("./reports/yrb_trends.csv", index_col="ID")
    df.iloc[0:0].to_csv('./reports/yrb_trends.csv')
    vcb = readFile('./data/historical/vcb.csv')
    vcbSub = vcb.loc[end:start]
    for i in reversed(range(len(vcbSub))):
        date = vcbSub.index.values[i]
        recommendYellowRedBlue2(str(date)[0:10])

testMARecommendation()
# testYRBRecommendation()

