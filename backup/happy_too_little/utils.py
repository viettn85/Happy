from icecream import ic
import logging
import sh
import glob
from common import getCsvFiles, readRawFile, readFile, getConfigParser
import pandas as pd
from datetime import timedelta

def getInvestingVolume(price, investingAmount, maxStock):
    stockVolume = round(investingAmount/price)
    if stockVolume > maxStock:
        stockVolume = maxStock
    stockVolume -= stockVolume % 50
    return stockVolume

def getTradeFee(value, tradeRate):
    return round(value * tradeRate, 0)

def selectStocks(year):
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SOURCE_LOCATION = BASED_DIR + parser.get('happy', 'source_location')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    NUMBER_OF_DAYS = int(parser.get('happy', 'active_days'))
    MIN_VOLUME = int(parser.get('happy', 'min_volume'))
    MIN_OPEN_PRICE = int(parser.get('happy', 'min_open_price'))
    MAX_OPEN_PRICE = int(parser.get('happy', 'max_open_price'))

    if len(getCsvFiles(SELECTED_STOCK_LOCATION)) > 0:
        sh.rm(glob.glob(SELECTED_STOCK_LOCATION + "*"))
    ic("Started selecting stocks...")
    csvFiles = getCsvFiles(SOURCE_LOCATION)
    # csvFiles = ["AAA.csv","APG.csv"]
    selected = []
    for file in csvFiles:
        df = readFile((SOURCE_LOCATION + "{}").format(file))
        df = df.loc[year]
        # ic("{} {} {} {} {} {} {}".format(len(df), NUMBER_OF_DAYS, df.Volume.mean(), MIN_VOLUME, df.Open.mean(), MIN_OPEN_PRICE, MAX_OPEN_PRICE))
        if(len(df) > NUMBER_OF_DAYS) and df.Volume.mean() > MIN_VOLUME and (df.Open.mean() > MIN_OPEN_PRICE and df.Open.mean() < MAX_OPEN_PRICE):
            df["Short"] = False
            df["Long"] = False
            df["Category"] = ""
            df["Recommendation"] = ""
            df["Action"] = ""
            selected.append(file)
            df.to_csv((SELECTED_STOCK_LOCATION + "{}").format(file))
    ic(selected)
    ic("Completed selecting stocks!")

def getPrice(record, strategy):
    if strategy == "OPEN":
        return record.Open
    elif strategy == "MEAN":
        return round((record.Open + record.Close)/2)
    else:
        return record.Close

def updateRec(dailyTrades, stock):
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    REC_FULL_LOCATION = BASED_DIR + parser.get('happy', 'rec_full_location')
    REC_ACTIONS_LOCATION = BASED_DIR + parser.get('happy', 'rec_actions_location')
    try:
        # ic("Update rec file for ", stock)
        df = readFile(REC_FULL_LOCATION + stock + "_rec.csv")
        df.loc[dailyTrades.index[0]] = dailyTrades.iloc[0]
        df.to_csv(REC_FULL_LOCATION + stock + "_rec.csv")
        df = df[df.Action.isin(["Sold", "Bought"])]
        df.to_csv(REC_ACTIONS_LOCATION + stock + "_rec_actions.csv")
    except Exception as ex:
        ic(ex)
        # ic("Create rec file for ", stock)
        dailyTrades.to_csv(REC_FULL_LOCATION + stock + "_rec.csv")
        dailyTrades = dailyTrades[dailyTrades.Action.isin(["Sold", "Bought"])]
        dailyTrades.to_csv(REC_ACTIONS_LOCATION + stock + "_rec_actions.csv")

def isNotAllowToBuy(stock, date):
    # Check if bought in 10 days ago
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    dailyReports = pd.read_csv(REPORT_LOCATION + "trade_report.csv", index_col="ID")
    stockReport = dailyReports[dailyReports.Stock == stock]
    if len(stockReport) > 0:
        stockReport.sort_values(by=['Date'], inplace=True)
        if stockReport.iloc[-1].Action == "Sell":
            return str(date + timedelta(-10))[0:10] <= stockReport.iloc[-1].Date
    return False
