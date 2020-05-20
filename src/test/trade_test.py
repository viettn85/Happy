import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from common import readFile, readReport, clearReports

from datetime import datetime
import pandas as pd
import math
# pd.options.mode.chained_assignment = None 

start = '2020-01-01'
# end = datetime.today().strftime("%Y-%m-%d")
end = '2020-05-19'
dates = pd.date_range(start, end).tolist()

rec = readFile('./reports/rec.csv')
budget = 30000
maxVolume = 100

def getTradeInfo(stock, date):
    historicalData = readFile('./data/historical/{}.csv'.format(stock))
    recentData = historicalData.loc[:date]
    tradeData = recentData.iloc[[-2]]
    return (str(tradeData.index.values[0])[0:10], tradeData.Close[0])

def getInvestingVolume(price, budget, maxVolume):
    stockVolume = round(budget/price)
    if stockVolume > maxVolume:
        stockVolume = maxVolume
    stockVolume -= stockVolume % 50
    return stockVolume

def sell(date, sellList, tradeList, portfolio, budget):
    for stock in sellList:
        if stock not in portfolio.Stock.values:
            continue
        boughtPrice = float(portfolio[portfolio.Stock == stock].Price[0])
        stockVolume = float(portfolio[portfolio.Stock == stock].Volume[0])
        portfolio.query('Stock != "{}"'.format(stock), inplace=True)
        (tradeDate, tradePrice) = getTradeInfo(stock, date)
        value = stockVolume * tradePrice
        tradeFee = round(value * 0.0025, 3)
        budget = round(budget + value - tradeFee, 3)
        profit = round((tradePrice - boughtPrice) * stockVolume - 2 * tradeFee, 3)
        trade = {
            "ID": tradeDate + "-" + stock,
            "Action": "Sell",
            "Date": tradeDate,
            "InvestingAmount": budget,
            "Price": tradePrice,
            "Profit": profit,
            "Stock": stock,
            "TradeFee": tradeFee,
            "Value": value,
            "Volume": stockVolume
        }
        tradeList.append(trade)
    return (portfolio, budget)

def buy(date, buyList, tradeList, portfolio, budget):
    newPortfolio = []
    for stock in buyList:
        if stock in portfolio.Stock:
            continue
        (tradeDate, tradePrice) = getTradeInfo(stock, date)
        stockVolume = getInvestingVolume(tradePrice, budget, maxVolume)
        if stockVolume == 0:
            continue
        value = stockVolume * tradePrice
        tradeFee = round(value * 0.0025, 3)
        budget = round(budget - value - tradeFee, 3)
        trade = {
            "ID": tradeDate + "-" + stock,
            "Action": "Buy",
            "Date": tradeDate,
            "InvestingAmount": budget,
            "Price": tradePrice,
            "Profit": 0,
            "Stock": stock,
            "TradeFee": tradeFee,
            "Value": value,
            "Volume": stockVolume
        }
        # print(trade)
        tradeList.append(trade)
        newPortfolio.append({
            "Stock": stock,
            "Date": tradeDate,
            "ID": tradeDate + "-" + stock,
            "Price": tradePrice,
            "Value": stockVolume * tradePrice,
            "Volume": stockVolume,
            "Sellable": False
        })
        # print(newPortfolio)
    if len(newPortfolio) > 0:
        portfolio = portfolio.append(pd.DataFrame(newPortfolio).set_index("ID"))
    return (portfolio, budget)

# START: Only for testing
def clearFileContent(file):
    df = readReport(file)
    df.iloc[0:0].to_csv(file)

def clearReports():
    clearFileContent('./reports/trade_report.csv')
    clearFileContent('./reports/portfolio.csv')

clearReports()

for date in dates:
    print(date)
    tradeList = []
    dfTrade = readReport('./reports/trade_report.csv')
    portfolio = readReport('./reports/portfolio.csv')
    if isinstance(rec.loc[date].Sell, str):
        (portfolio, budget) = sell(date, rec.loc[date].Sell.split('|'), tradeList, portfolio, budget)
    if isinstance(rec.loc[date].Buy, str):
        (portfolio, budget) = buy(date, rec.loc[date].Buy.split('|'), tradeList, portfolio, budget)
    if len(tradeList) == 0:
        continue
    dfTrade = dfTrade.append(pd.DataFrame(tradeList).set_index("ID"))
    # print(dfTrade)
    dfTrade.to_csv('./reports/trade_report.csv')
    portfolio.to_csv('./reports/portfolio.csv')


dfTrade = readReport('./reports/trade_report.csv')
portfolio = readReport('./reports/portfolio.csv')

print("Start 30000")
print("No of Trades {}".format(len(dfTrade)))
print(dfTrade.iloc[-1].InvestingAmount, portfolio.Value.sum())
print("End {}".format(round(dfTrade.iloc[-1].InvestingAmount + portfolio.Value.sum(),3)))
