from recommendation import categorizeCandle, recommendDaily
from utils import getInvestingVolume, getTradeFee, getPrice, updateRec
from common import readFile, getConfigParser
import pandas as pd
import functools
from icecream import ic
from datetime import datetime


def analyzePattern(df, date, stock, dailyDf, portfolio, investingMoney, investingAmount):
    if not df.loc[str(date)].empty:
        positions = df.index.get_loc(str(date))
        if len(positions) > 0 and positions[0] < len(df) - 1:
            # ic(date)
            parser = getConfigParser()
            MAX_VOLUME = int(parser.get('happy', 'max_volume'))
            TRADE_RATE = float(parser.get('happy', 'trade_rate'))
            TRADE_STRATEGY = parser.get('happy', 'trade_strategy')
            position = positions[0]
            df.Short.iloc[position] = df.iloc[position].Change < 1;
            df.Long.iloc[position] = df.iloc[position].Change >= 5;
            categorizeCandle(df, position);
            recommendDaily(df, position, stock, portfolio);
            # ic(df.loc[[df.index[position]]])
            updateRec(df.loc[[df.index[position]]], stock);
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
                        price = getPrice(df.iloc[position], TRADE_STRATEGY);
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
                price = getPrice(df.iloc[position], TRADE_STRATEGY);
                stockVolume = getInvestingVolume(price, investingMoney, investingAmount, MAX_VOLUME)
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
            
    return (dailyDf, portfolio, investingMoney, investingAmount)

def analyzeAll(date, files, dailyReports, dailyDf, portfolio, investingMoney, investingAmount):
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    for file in files:    
        df = readFile((SELECTED_STOCK_LOCATION + "{}").format(file));
        df['Action'] = df.Action.astype(str)
        df['Categories'] = df.Categories.astype(str)
        df['Recommendation'] = df.Recommendation.astype(str)
        (dailyDf, portfolio, investingMoney, investingAmount) = analyzePattern(df, date, file[0:3], dailyDf, portfolio, investingMoney, investingAmount)
        df.to_csv(SELECTED_STOCK_LOCATION + "{}".format(file))
    if len(dailyDf) > 0:
        finalDf = functools.reduce(lambda a,b : a.append(b),dailyDf)
        dailyReports = dailyReports.append(finalDf)
        dailyReports.to_csv(REPORT_LOCATION + "reports.csv", index=True)
    portfolio.to_csv(REPORT_LOCATION + "portfolio.csv",index=True)
    return (dailyReports, dailyDf, portfolio, investingMoney, investingAmount)
