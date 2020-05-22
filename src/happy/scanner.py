import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile, readReport
import logging
import logging.config
from datetime import datetime
from mbs import getSecurityList
from utils import calculateMAs

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")

def updatePrices():
    portfolio = readReport('./reports/real_portfolio.csv')
    interestedList = ['ITA','FPT','HVN','PVB','HAG','PVS','PVT','POW','HSG']
    stocks = ",".join(list(portfolio.Stock.values) + interestedList)
    df = getSecurityList(stocks)
    for i in range(len(df)):
        detail = df.iloc[i]
        logger.info("Updating prices for {} on {}".format(detail.Stock, today))
        currentDf = pd.DataFrame([{
            "Date": today,
            'Close': int(detail.Price)/100,
            'Open': int(detail.Reference)/100,
            'High': int(detail.High)/100,
            'Low': int(detail.Low)/100,
            'Change': 0.0,
            'Volume': 0,
            'MA3': 0.0,
            'MA8': 0.0,
            'MA20': 0.0,
            'MA3_8': 0.0,
            'MA3_20': 0.0,
            'MA8_20': 0.0,
            'Short': False,
            'Long': False,
            'Category': '',
            'Recommendation': '',
            'Action': ''
        }])
        currentDf['Date'] = pd.to_datetime(currentDf['Date'])
        currentDf.set_index('Date', inplace=True)
        dailyDf = readFile('./data/daily/{}.csv'.format(detail.Stock))
        dailyDf = currentDf.append(dailyDf)
        dailyDf.sort_index(ascending=True,inplace=True)
        # print(detail.Stock)
        # print(currentDf.Close[0])
        calculateMAs(dailyDf)
        dailyDf.sort_index(ascending=False,inplace=True)
        dailyDf.to_csv('./data/daily/{}.csv'.format(detail.Stock))
        logger.info("Finished Updating prices for {} on {}".format(detail.Stock, today))

if __name__ == '__main__':
    updatePrices()
