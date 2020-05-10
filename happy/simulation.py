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
YEAR = parser.get('happy', 'year')
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
DATE_LIST = pd.date_range(start=parser.get('happy', 'start_date'),end=parser.get('happy', 'end_date'))

totalMoney = 100000000

def simulateDaily():
    investingMoney = 0
    investingAmount = 500000000
    for d in DATE_LIST:
        portfolio = pd.read_csv(REPORT_LOCATION + "portfolio.csv", index_col="Stock")
        dailyReports = pd.read_csv(REPORT_LOCATION + "reports.csv", index_col="ID")
        dailyDf = []
        (dailyReports, dailyDf, portfolio, investingMoney, investingAmount) = analyzeAll(d, getCsvFiles(SELECTED_STOCK_LOCATION), dailyReports, dailyDf, portfolio, investingMoney, investingAmount);
        # stockList = ['MBG.csv','HDC.csv','DRC.csv','TNG.csv','SBT.csv','APG.csv','CII.csv','AAA.csv','DXG.csv','PDR.csv','DPM.csv']
        # stockList = ['CII.csv']
        # (dailyReports, dailyDf, portfolio, investingMoney, investingAmount) = analyzeAll(d, stockList, dailyReports, dailyDf, portfolio, investingMoney, investingAmount);

# preproceed(SOURCE_LOCATION, D3_DATA)
clearRecFolders()
clearReports()
# selectStocks(YEAR);
simulateDaily();
