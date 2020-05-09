import pandas as pd
from datetime import datetime
import sys
sys.path.insert(1, '../utils')
from common import getCsvFiles, readRawFile, readFile
from shutil import copyfile
import os
import glob
import sh
import functools
pd.options.mode.chained_assignment = None 

from icecream import ic
import logging

BASED_DIR = "/Users/viet_tran/Workplace/Practice/VNStock/"
LOG_FILENAME = BASED_DIR + 'logs/happy.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

dateList = pd.date_range(start="2020-01-01",end="2020-05-05")
SOURCE_LOCATION = BASED_DIR + "raw_data/"
SELECTED_STOCK_LOCATION = BASED_DIR + "selected_stocks/"
REPORT_LOCATION = BASED_DIR + "reports/"
REC_FULL_LOCATION = BASED_DIR + "rec/"
REC_ACTIONS_LOCATION = BASED_DIR + "rec_actions/"
D3_DATA = BASED_DIR + "d3_data/"
YEAR = "2020"
NUMBER_OF_DAYS = 60
MIN_VOLUME = 500000
MIN_OPEN_PRICE = 8000
MAX_OPEN_PRICE = 40000
TRADE_RATE = 0.002
rates = 8

havingStock = None
totalMoney = 100000000
investingMoney = 0
investingAmount = 300000000
dailyDf = []
dailyReports = None
maxStock = 2000


def isRed(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Open > c.Close;

def isGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Close > c.Open;

def isFull(high, top, bottom, low): # Use to check if the canlde stills if full both sides
    return (top - bottom) > rates * (high - top) and (top - bottom) > rates * (bottom - low);

def isTopFull(high, top, bottom, low):
    return (top - bottom) > rates * (high - top) and (top - bottom) <= rates * (bottom - low)

def isBottomFull(high, top, bottom, low):
    return (top - bottom) <= rates * (high - top) and (top - bottom) > rates * (bottom - low)

def isLongGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Close > c.Open and c.Change >= 7

def isFullRed(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isFull(c.High, c.Open, c.Close, c.Low)

def isFullGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isFull(c.High, c.Close, c.Open, c.Low)

def isUpRed(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isTopFull(c.High, c.Open, c.Close, c.Low);

def isUpGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isTopFull(c.High, c.Close, c.Open, c.Low)

def isDownRed(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isBottomFull(c.High, c.Open, c.Close, c.Low)

def isDownGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isBottomFull(c.High, c.Close, c.Open, c.Low)


def categorizeCandle(df, position):
    categories = []
    if df.iloc[position].Short:
        df["Categories"][position] = "Short"
        return
    if df.iloc[position].Long:
        categories.append("Long");
    if isRed(df, position):
        categories.append("Red");
    if isUpRed(df, position):
        categories.append("Up Red");
    if isFullRed(df, position):
        categories.append("Full Red");
    if isDownRed(df, position):
        categories.append("Down Red");
    if isGreen(df, position):
        categories.append("Green");
    if isUpGreen(df, position):
        categories.append("Up Green");
    if isFullGreen(df, position):
        categories.append("Full Green");
    if isDownGreen(df, position):
        categories.append("Down Green");
    df["Categories"][position] = "|".join(categories)


def recommendDaily(df, position):
    recommendations = [];
    c = df.iloc[position];
    p = df.iloc[position + 1];
    if isLongGreen(df, position):
        recommendations.append("LongGreenCode")
    if isFullGreen(df, position) and df.iloc[position].Change > 3:
        recommendations.append("FullGreenCode")
    if isFullRed(df, position):
        recommendations.append("FullRedCode")
        recommendations.append("Sell");
    if isUpGreen(df, position) and df.iloc[position].Change > 3:
        recommendations.append("UpGreenCode")
    if isDownRed(df, position):
        recommendations.append("DownRedCode")
        recommendations.append("Sell");
    if "UpGreenCode" in p.Recommendation:
        if ("Red" not in c.Categories) and (not c.Short):
            recommendations.append("Buy")
    if "DownRedCode" in p.Recommendation:
        recommendations.append("Sell")
    if "FullGreenCode" in p.Recommendation:
        if c.Open >= c.Close:
            recommendations.append("Sell");
        else: 
            if c.Short:
                recommendations.append("FullGreenCode")
            else:
                recommendations.append("Buy")

    if "FullRedCode" in p.Recommendation:
        recommendations.append("Sell")
    df["Recommendation"][position] = "|".join(recommendations)
    actions = []
    if "Sell" in recommendations:
        actions.append("Sell")
    if "Buy" in recommendations:
        actions.append("Buy")
    df.Action.iloc[position] = "|".join(actions)


def getInvestingVolume(price):
    if(investingAmount - investingMoney) < 10000000:
        return 0;
    stockVolume = round((investingAmount - investingMoney)/price);
    if stockVolume > maxStock:
        stockVolume = maxStock
    stockVolume -= stockVolume % -50
    return stockVolume;

def getTradeFee(value):
    return round(value * TRADE_RATE, 0)


def analyzePattern(df, date, stock):
    if not df.loc[str(date)].empty:
        positions = df.index.get_loc(str(date))
        if len(positions) > 0 and positions[0] < len(df) - 1:
            global investingAmount
            global investingMoney
            global havingStock
            global dailyDf
            position = positions[0]
            df.Short.iloc[position] = df.iloc[position].Change < 1;
            df.Long.iloc[position] = df.iloc[position].Change >= 5;
            categorizeCandle(df, position);
            recommendDaily(df, position);
            if df.iloc[position].Action == "Buy" and (stock not in havingStock.index):
                price = df.iloc[position].Open
                stockVolume = getInvestingVolume(price)
                if stockVolume > 0:
                    investingMoney = investingMoney + stockVolume * price;
                    investingAmount = investingAmount - stockVolume * price - getTradeFee(stockVolume * price);
                    report = {
                        "ID": [str(date)[0:10] + "-" + stock],
                        "Date": [date],
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
                    havingStock = havingStock.append(newStock)
                    print("Buy {} {} with price {} on {}".format(stockVolume, stock, price, str(date)[0:10]))
            if df.iloc[position].Action == "Sell" and (stock in havingStock.index):
                price = df.iloc[position].Open
                stockVolume = havingStock.loc[stock].Volume
                investingMoney = investingMoney - stockVolume * price;
                investingAmount = investingAmount + stockVolume * price  - getTradeFee(stockVolume * price);
                profit = (price - havingStock.loc[stock].Price) * stockVolume
                report = {
                    "ID": [str(date)[0:10] + "-" + stock],
                    "Date": [date],
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
                havingStock.drop(stock, inplace=True)
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
    havingStock.to_csv(REPORT_LOCATION + "portfolio.csv",index=True)

def simulateDaily():
    global havingStock
    global dailyDf
    global dailyReports
    for d in dateList:
        havingStock = pd.read_csv(REPORT_LOCATION + "portfolio.csv", index_col="Stock")
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

# havingStock = pd.read_csv("../having_stocks.csv", index_col="Stock")
# print(havingStock)
