import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/utils')

import pandas as pd
from common import getConfigParser, readFile
from utils import getInvestingVolume, getTradeFee, selectStocks
from analysis import analyzeAll
from icecream import ic
from mbs import getSecurityList
from datetime import datetime
from const import *
from categorization import categorizeCandle

import logging
import logging.config


from configparser import ConfigParser
parser = getConfigParser()

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
pd.options.mode.chained_assignment = None 

BASED_DIR = parser.get('happy', 'based_dir')
SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
DAILY_SCAN = BASED_DIR + parser.get('happy', 'daily_scan')

def scanNightTime(date):
    # ic(date)
    logger.info('Start nightly scanning on {}'.format(date))
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    logger.info("Start night scan on {}".format(date))
    investingAmount = int(parser.get('happy', 'investing_money'))
    portfolio = pd.read_csv(REPORT_LOCATION + "portfolio.csv", index_col="Stock")
    # (portfolio, investingAmount) = analyzeAll(date, getCsvFiles(SELECTED_STOCK_LOCATION), portfolio, investingAmount)
    # stockList = ['MBG.csv','HDC.csv','DRC.csv','TNG.csv','SBT.csv','APG.csv','CII.csv','AAA.csv','DXG.csv','PDR.csv','DPM.csv']
    stockList = ['MBG.csv']
    (portfolio, investingAmount) = analyzeAll(date, stockList, portfolio, investingAmount)
    logger.info('Ended nightly scanning on {}'.format(date))

def scanDayTime(date):
    logger.info('Start daily scanning on {}'.format(date))
    recReport = readFile(REPORT_LOCATION + "stock_rec_report.csv")
    ic(recReport.tail())
    stockToBuy = recReport.loc[date].BuyNew[0].split("|") if str(recReport.loc[date].BuyNew[0]) != 'nan' else []
    stockToSell = recReport.loc[date].Sell[0].split("|") if str(recReport.loc[date].Sell[0]) != 'nan' else []
    stocks = stockToBuy + stockToSell
    df = getSecurityList(stocks)
    df['Category'] = ""
    for i in range(len(df)):
        categorizeCandle(df, i)
    df.to_csv('{}{}.csv'.format(DAILY_SCAN,datetime.now().strftime('%Y-%m-%d %H:%M:%S')), index=None)
    logger.info('Ended daily scanning on {}'.format(date))
