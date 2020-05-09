from recommendation import categorizeCandle, recommendDaily
from utils import getInvestingVolume, getTradeFee
from common import readFile, getConfigParser
import pandas as pd
import functools

def analyzePattern(df, date, stock, dailyDf, portfolio, investingMoney, investingAmount):
    if not df.loc[str(date)].empty:
        positions = df.index.get_loc(str(date))
        if len(positions) > 0 and positions[0] < len(df) - 1:
            parser = getConfigParser()
            MAX_VOLUME = int(parser.get('happy', 'max_volume'))
            TRADE_RATE = float(parser.get('happy', 'trade_rate'))
            position = positions[0]
            df.Short.iloc[position] = df.iloc[position].Change < 1;
            df.Long.iloc[position] = df.iloc[position].Change >= 5;
            categorizeCandle(df, position);
            recommendDaily(df, position);
            if df.iloc[position].Action == "Buy" and (stock not in portfolio.index):
                price = df.iloc[position].Open
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
    return (dailyDf, portfolio, investingMoney, investingAmount)

def analyzeAll(date, files, dailyReports, dailyDf, portfolio, investingMoney, investingAmount):
    for file in files:
        parser = getConfigParser()
        BASED_DIR = parser.get('happy', 'based_dir')
        SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
        REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
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