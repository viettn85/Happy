from recommendation import categorizeCandle, defineDailyAction, recommendStock
from utils import getInvestingVolume, getTradeFee, getPrice, updateRec, isNotAllowToBuy
from common import readFile, getConfigParser
import pandas as pd
import functools
from icecream import ic
from datetime import datetime


def analyzePattern(df, date, stock, dailyTrades, portfolio, investingAmount):
    if not df.loc[str(date)].empty:
        positions = df.index.get_loc(str(date))
        if len(positions) > 0 and positions[0] < len(df) - 1:
            # ic(date)
            parser = getConfigParser()
            MAX_VOLUME = int(parser.get('happy', 'max_volume'))
            TRADE_RATE = float(parser.get('happy', 'trade_rate'))
            TRADE_STRATEGY = parser.get('happy', 'trade_strategy')
            position = positions[0]
            df.Short.iloc[position] = df.iloc[position].Change < 1
            df.Long.iloc[position] = df.iloc[position].Change >= 5
            categorizeCandle(df, position)
            defineDailyAction(df, position, stock, portfolio)
            # ic(df.loc[[df.index[position]]])
            updateRec(df.loc[[df.index[position]]], stock)
            # Sold the stock on portfolio
            if (stock in portfolio.index) and "Sold" in df.iloc[position].Action:
                p = df.iloc[position + 1]
                stockVolume = portfolio.loc[stock].Volume
                # currentDate = datetime.strptime(date, '%Y-%m-%d')
                boughtDate = datetime.strptime(portfolio.loc[stock].Date, '%Y-%m-%d')
                if (date - boughtDate).days < 3:
                    ic("Waiting...{} {} {}".format(date, portfolio.loc[stock].Date, (date - boughtDate).days))
                    df.Action.iloc[position] = df.Action.iloc[position] + "| Will Sell as Waiting for T3"
                else:
                    if "Cut Loss" in p.Recommendation:
                        price = round(df.iloc[position].Close/2 + df.iloc[position].Open/2)
                        ic("Sold as Cut Loss {}".format(date))
                    elif "Overcome Profit" in p.Recommendation:
                        price = round(df.iloc[position].Close/2 + df.iloc[position].Open/2)
                        ic("Sold as Overcome Profit {}".format(date))
                    else: 
                        price = getPrice(df.iloc[position], TRADE_STRATEGY)
                    tradeFee = getTradeFee(stockVolume * price, TRADE_RATE)
                    investingAmount = investingAmount + stockVolume * price  - tradeFee
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
                        "TradeFee": [tradeFee],
                        "InvestingAmount": [investingAmount]
                    }
                    stockReportDf = pd.DataFrame.from_dict(report)
                    stockReportDf.set_index("ID", inplace=True)
                    dailyTrades.append(stockReportDf)
                    # When allow multiple buys on one stock, the drop statement need to be updated: drop by ID instead of Stock
                    portfolio.drop(stock, inplace=True)
                    ic("Sold", stock, stockVolume, price, str(date)[0:10])
            # Check stock existing on portfolio without Sold Recommendation:
            ## 1. Will SELL if overprofit
            ## 2. Will SELL if 
            if (stock in portfolio.index) and ("Sold" not in df.iloc[position].Action):
                if "Cut Loss" in df.iloc[position].Action:
                    ic("Sell as Cut Loss")
                if "Overcome Profit" in df.iloc[position].Action:
                    ic("Sell as Overcome Profit")
            if "Bought" in df.iloc[position].Action and (stock not in portfolio.index):
                # price = df.iloc[position].Open
                price = getPrice(df.iloc[position], TRADE_STRATEGY)
                stockVolume = getInvestingVolume(price, investingAmount, MAX_VOLUME)
                if stockVolume > 0:
                    tradeFee = getTradeFee(stockVolume * price, TRADE_RATE)
                    investingAmount = investingAmount - stockVolume * price - tradeFee
                    report = {
                        "ID": [str(date)[0:10] + "-" + stock],
                        "Date": [str(date)[0:10]],
                        "Stock": [stock],
                        "Action": ["Buy"],
                        "Volume": [stockVolume],
                        "Price": [price],
                        "Value": [stockVolume * price],
                        "Profit": [0],
                        "TradeFee": [tradeFee],
                        "InvestingAmount": [investingAmount]
                    }
                    stockReportDf = pd.DataFrame.from_dict(report)
                    stockReportDf.set_index("ID", inplace=True)
                    dailyTrades.append(stockReportDf)
                    newStock = pd.DataFrame.from_dict({
                        "ID": [str(date)[0:10] + "-" + stock],
                        "Date":[str(date)[0:10]], 
                        "Stock": [stock], 
                        "Price": [price], 
                        "Volume": [stockVolume], 
                        "Value": [stockVolume * price]
                    })
                    newStock.set_index("Stock", inplace=True)
                    portfolio = portfolio.append(newStock)
                    ic("Bought", stock, stockVolume, price, str(date)[0:10])
            
    return (dailyTrades, portfolio, investingAmount)

def analyzeAll(date, files, portfolio, investingAmount):
    dailyTrades = []
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    stocksToSell = []
    stocksToBuyNew = []
    stocksToBuyMore = []
    for file in files:
        stock = file[0:3]
        df = readFile((SELECTED_STOCK_LOCATION + "{}").format(file))
        df['Action'] = df.Action.astype(str)
        df['Category'] = df.Category.astype(str)
        df['Recommendation'] = df.Recommendation.astype(str)
        positions = df.index.get_loc(str(date))
        if isNotAllowToBuy(stock, date):
            if len(positions) > 0:
                ic("Not Allow To trade")
                df.Action.iloc[positions[0]] = "Relax"
                df.Recommendation.iloc[positions[0]] = "Not Trade Today"
        else:
            (dailyTrades, portfolio, investingAmount) = analyzePattern(df, date, stock, dailyTrades, portfolio, investingAmount)
        df.to_csv(SELECTED_STOCK_LOCATION + "{}".format(file))
        if len(positions) > 0:
            if recommendStock(df, positions[0]) == 'Sell' and stock in portfolio.index:
                stocksToSell.append(stock)
            if recommendStock(df, positions[0]) == 'Buy' and stock in portfolio.index:
                stocksToBuyMore.append(stock)
            if recommendStock(df, positions[0]) == 'Buy' and stock not in portfolio.index:
                stocksToBuyNew.append(stock)

    currentRecReport = pd.read_csv(REPORT_LOCATION + "stock_rec_report.csv", index_col="Date")
    recReport = pd.DataFrame.from_dict({
        "Date": [str(date)[0:10]],
        "Sell": ["|".join(stocksToSell)],
        "BuyNew": ["|".join(stocksToBuyNew)],
        "BuyMore": ["|".join(stocksToBuyMore)]  
    })
    recReport.set_index("Date", inplace=True)
    # ic(recReport)
    currentRecReport = currentRecReport.append(recReport)
    currentRecReport.to_csv(REPORT_LOCATION + "stock_rec_report.csv", index=True)
    if len(dailyTrades) > 0:
        finalDf = functools.reduce(lambda a,b : a.append(b),dailyTrades)
        dailyReports = pd.read_csv(REPORT_LOCATION + "trade_report.csv", index_col="ID")
        dailyReports = dailyReports.append(finalDf)
        dailyReports.to_csv(REPORT_LOCATION + "trade_report.csv", index=True)
    portfolio.to_csv(REPORT_LOCATION + "portfolio.csv",index=True)
    return (portfolio, investingAmount)
