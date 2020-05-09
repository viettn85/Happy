import pandas as pd
from common import getCsvFiles, readRawFile, readFile
import os
import sh
import glob
import functools
pd.options.mode.chained_assignment = None 

from recommendation import recommendDaily, categorizeCandle
from utils import getInvestingVolume, getTradeFee
from icecream import ic
import logging

from configparser import ConfigParser

parser = ConfigParser()
parser.read('happy.ini')


BASED_DIR = parser.get('happy', 'based_dir')
SOURCE_LOCATION = BASED_DIR + parser.get('happy', 'source_location')
SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
REC_FULL_LOCATION = BASED_DIR + parser.get('happy', 'rec_full_location')
REC_ACTIONS_LOCATION = BASED_DIR + parser.get('happy', 'rec_actions_location')
D3_DATA = BASED_DIR + parser.get('happy', 'd3_data')
LOG_FILENAME = BASED_DIR + parser.get('happy', 'log_filename')

YEAR = parser.get('happy', 'year')
NUMBER_OF_DAYS = int(parser.get('happy', 'active_days'))
MIN_VOLUME = int(parser.get('happy', 'min_volume'))
MIN_OPEN_PRICE = int(parser.get('happy', 'min_open_price'))
MAX_OPEN_PRICE = int(parser.get('happy', 'max_open_price'))
TRADE_RATE = float(parser.get('happy', 'trade_rate'))

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
DATE_LIST = pd.date_range(start=parser.get('happy', 'start_date'),end=parser.get('happy', 'end_date'))

portfolio = None
totalMoney = 100000000
investingMoney = 0
investingAmount = 300000000
dailyDf = []
dailyReports = None
maxStock = 2000


def analyzePattern(df, date, stock):
    if not df.loc[str(date)].empty:
        positions = df.index.get_loc(str(date))
        if len(positions) > 0 and positions[0] < len(df) - 1:
            global investingAmount
            global investingMoney
            global portfolio
            global dailyDf
            position = positions[0]
            df.Short.iloc[position] = df.iloc[position].Change < 1;
            df.Long.iloc[position] = df.iloc[position].Change >= 5;
            categorizeCandle(df, position);
            recommendDaily(df, position);
            if df.iloc[position].Action == "Buy" and (stock not in portfolio.index):
                price = df.iloc[position].Open
                stockVolume = getInvestingVolume(price, investingMoney, investingAmount, maxStock)
                if stockVolume > 0:
                    investingMoney = investingMoney + stockVolume * price;
                    investingAmount = investingAmount - stockVolume * price - getTradeFee(stockVolume * price, TRADE_RATE);
                    report = {
                        "ID": [str(date)[0:10] + "-" + stock],
                        "Date": [str(date)[0:10]],
                        "Stock": [stock],
                        "Action": ["Buy"],
                        "Volume": [stockVolume],
                        "Price": [price],
                        "Value": [stockVolume * price],
                        "Profit": [0],
                        "investingMoney": [investingMoney],
                        "investingAmount": [investingAmount]
                    }
                    stockReportDf = pd.DataFrame.from_dict(report)
                    stockReportDf.set_index("ID", inplace=True)
                    dailyDf.append(stockReportDf)
                    newStock = pd.DataFrame.from_dict({"Stock": [stock], "Price": [price], "Volume": [stockVolume], "Value": [stockVolume * price]})
                    newStock.set_index("Stock", inplace=True)
                    portfolio = portfolio.append(newStock)
                    print("Buy {} {} with price {} on {}".format(stockVolume, stock, price, str(date)[0:10]))
            if df.iloc[position].Action == "Sell" and (stock in portfolio.index):
                price = df.iloc[position].Open
                stockVolume = portfolio.loc[stock].Volume
                investingMoney = investingMoney - stockVolume * price;
                investingAmount = investingAmount + stockVolume * price  - getTradeFee(stockVolume * price, TRADE_RATE);
                profit = (price - portfolio.loc[stock].Price) * stockVolume
                report = {
                    "ID": [str(date)[0:10] + "-" + stock],
                    "Date": [str(date)[0:10]],
                    "Stock": [stock],
                    "Action": ["Sell"],
                    "Volume": [stockVolume],
                    "Price": [price],
                    "Value": [stockVolume * price],
                    "Profit": [profit],
                    "investingMoney": [investingMoney],
                    "investingAmount": [investingAmount]
                }
                stockReportDf = pd.DataFrame.from_dict(report)
                stockReportDf.set_index("ID", inplace=True)
                dailyDf.append(stockReportDf)
                portfolio.drop(stock, inplace=True)
                print("Sell {} {} with price {} and profit {} on {}".format(stockVolume, stock, price, profit, str(date)[0:10]))

def analyzeAll(date, files):
    for file in files:
        df = readFile((SELECTED_STOCK_LOCATION + "{}").format(file));
        df['Action'] = df.Action.astype(str)
        df['Categories'] = df.Categories.astype(str)
        df['Recommendation'] = df.Recommendation.astype(str)
        analyzePattern(df, date, file[0:3])
        df.to_csv(SELECTED_STOCK_LOCATION + "{}".format(file))
    if len(dailyDf) > 0:
        finalDf = functools.reduce(lambda a,b : a.append(b),dailyDf)
        global dailyReports
        dailyReports = dailyReports.append(finalDf)
        dailyReports.to_csv(REPORT_LOCATION + "reports.csv", index=True)
    portfolio.to_csv(REPORT_LOCATION + "portfolio.csv",index=True)

def simulateDaily():
    global portfolio
    global dailyDf
    global dailyReports
    for d in DATE_LIST:
        portfolio = pd.read_csv(REPORT_LOCATION + "portfolio.csv", index_col="Stock")
        dailyReports = pd.read_csv(REPORT_LOCATION + "reports.csv", index_col="ID")
        dailyDf = []
        analyzeAll(d, getCsvFiles(SELECTED_STOCK_LOCATION));


def selectFiles(year):
    if len(getCsvFiles(SELECTED_STOCK_LOCATION)) > 0:
        sh.rm(glob.glob(SELECTED_STOCK_LOCATION + "*"))
    ic("Started selecting stocks...")
    csvFiles = getCsvFiles(SOURCE_LOCATION);
    # csvFiles = ["AAA.csv","APG.csv"]
    selected = []
    for file in csvFiles:
        df = readFile((SOURCE_LOCATION + "{}").format(file));
        df = df.loc[year]
        if(len(df) > NUMBER_OF_DAYS) and df.Volume.mean() > MIN_VOLUME and (df.Open.mean() > MIN_OPEN_PRICE and df.Open.mean() < MAX_OPEN_PRICE):
            df["Short"] = False
            df["Long"] = False
            df["Categories"] = ""
            df["Recommendation"] = ""
            df["Action"] = ""
            df.to_csv((SELECTED_STOCK_LOCATION + "{}").format(file))
    ic("Completed selecting stocks!")

def preproceed(location, d3Data):
    logging.info("Started preproceeding process...")
    ic("Started preproceeding process...")
    csvFiles = getCsvFiles(location);
    for f in csvFiles:
        df = readRawFile((location + f));
        if not {'Date', 'Close', "High", "Low", "Open", "Volume"}.issubset(df.columns):
            os.remove(location + f)
            ic("Removed", f)
            logging.info("Removed raw stock {}".format(f))
            continue
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index("Date", inplace=True)
        df.sort_index(ascending=False, inplace=True)
        df["Change"] = round(abs(df.Close - df.Open)/df.Open * 100, 2);
        df = df[["Close", "Open", "High", "Low", "Change", "Volume"]]
        df.to_csv(location + f)
        df.sort_index(ascending=True, inplace=True)
        df.to_csv(d3Data + f)
    logging.info("Completed preproceeding process...")
    ic("Completed preproceeding process...")

# Only for testing
def clearFileContent(file):
    df = readRawFile(file);
    df.iloc[0:0].to_csv(file,index=None)
def clearReports():
    clearFileContent(REPORT_LOCATION + "reports.csv")
    clearFileContent(REPORT_LOCATION + "portfolio.csv")



# preproceed(SOURCE_LOCATION, D3_DATA)
clearReports()
selectFiles(YEAR);
simulateDaily();

# portfolio = pd.read_csv("../having_stocks.csv", index_col="Stock")
# print(portfolio)
