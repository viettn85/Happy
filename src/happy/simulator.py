import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/utils')

import pandas as pd
from common import *
from utils import getInvestingVolume, getTradeFee, selectStocks
from analysis import analyzeAll
from icecream import ic
import logging
from configparser import ConfigParser


parser = getConfigParser()
pd.options.mode.chained_assignment = None 

BASED_DIR = parser.get('happy', 'based_dir')
D3_DATA = BASED_DIR + parser.get('happy', 'd3_data')
SOURCE_LOCATION = BASED_DIR + parser.get('happy', 'source_location')
SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
LOG_FILENAME = BASED_DIR + parser.get('happy', 'log_filename')
START_DATE = parser.get('happy', 'start_date')
END_DATE = parser.get('happy', 'end_date')
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
DATE_LIST = pd.date_range(start=parser.get('happy', 'start_date'),end=parser.get('happy', 'end_date'))

totalMoney = 100000000

def simulateDaily():
    investingAmount = int(parser.get('happy', 'investing_money'))
    for date in DATE_LIST:
        # ic(date)
        portfolio = pd.read_csv(REPORT_LOCATION + "portfolio.csv", index_col="Stock")
        # (portfolio, investingAmount) = analyzeAll(date, getCsvFiles(SELECTED_STOCK_LOCATION), portfolio, investingAmount)
        # stockList = ['MBG.csv','HDC.csv','DRC.csv','TNG.csv','SBT.csv','APG.csv','CII.csv','AAA.csv','DXG.csv','PDR.csv','DPM.csv']
        stockList = ['MBG.csv']
        (portfolio, investingAmount) = analyzeAll(date, stockList, portfolio, investingAmount)

def showResults():
    dailyReports = pd.read_csv(REPORT_LOCATION + "trade_report.csv", index_col="ID")
    portfolio  = pd.read_csv(REPORT_LOCATION + "portfolio.csv",index_col="Stock")
    if len(dailyReports) > 0:
        total = dailyReports.iloc[-1].InvestingAmount + portfolio.Value.sum()
        ic(dailyReports.iloc[-1].InvestingAmount)
        ic(portfolio.Value.sum())
        ic(total)

# preproceed(SOURCE_LOCATION, D3_DATA)
selectStocks(START_DATE, END_DATE)
clearRecFolders()
clearReports()
simulateDaily()
showResults()