import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile, readReport
import logging
import logging.config
from datetime import datetime

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

duration = 10
threshold = 8


def searchTrend(date):
    logger.info("Started recommendation process on {}".format(date))
    csvFiles = getCsvFiles("./data/historical/")
    stocks = []
    for f in csvFiles:
        stock = f[0:3]
        df = readFile(("./data/daily/" + f))
        df = df.loc[date:]
        if len(df) < duration:
            continue
        count = 0
        for i in range(duration - 1):
            current = df.iloc[i]
            previous = df.iloc[i+1]
            if current.Blue < previous.Blue:
                count = count + 1
        if count > threshold:
            stocks.append(stock)
    if len(stocks) > 0:
        return pd.DataFrame([{'Date': date, "Stocks": '|'.join(stocks)}])
    else:
        return pd.DataFrame([])

def searchTrend2019():
    start = '2019-01-01'
    end = '2019-12-31'
    vcb = readFile('./data/historical/vcb.csv')
    vcbSub = vcb.loc[end:start]
    dfList = []
    for i in reversed(range(len(vcbSub))):
        date = vcbSub.index.values[i]
        dfList.append(searchTrend(str(date)[0:10]))
    df = pd.concat(dfList)
    df.to_csv('./reports/downtrends_2019.csv')

if __name__ == '__main__':
    searchTrend2019()
    date = datetime.today().strftime("%Y-%m-%d")
    print(searchTrend(date))
