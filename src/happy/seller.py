import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/utils')

from common import getConfigParser, readFile, getCsvFiles
from categorization import categorizeCandle
from icecream import ic
import glob
import os
import logging
import logging.config
import pandas as pd

from configparser import ConfigParser
parser = getConfigParser()

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

BASED_DIR = parser.get('happy', 'based_dir')
DAILY_SCAN = BASED_DIR + parser.get('happy', 'daily_scan')
REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')


def sell():
    portfolio = getPortfolio()
    ic(portfolio)
    newPrices = getLastestPrice()
    ic(newPrices)
    mergedDf = newPrices.merge(portfolio, left_index=True, right_on='Stock')
    ic(mergedDf)
    sellableDf = mergedDf[mergedDf.Category.isin(['Up Red','Full Red'])]
    ic(sellableDf.info())

def getLastestPrice():
    csvList = glob.glob(DAILY_SCAN + "*") # * means all if need specific format then *.csv
    latestFile = max(csvList, key=os.path.getctime)
    newPrices = pd.read_csv(latestFile, index_col="Stock")
    return pd.read_csv(latestFile, index_col="Stock")

def getPortfolio():
    portfolio = readFile(REPORT_LOCATION + "portfolio.csv")
    return portfolio[portfolio.Sellable]


sell()