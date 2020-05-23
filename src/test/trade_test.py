import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from common import readFile, readReport, clearReports

from datetime import datetime
import pandas as pd
import math
# pd.options.mode.chained_assignment = None 

start = '2019-01-01'
# end = datetime.today().strftime("%Y-%m-%d")
end = '2019-12-31'
dates = pd.date_range(start, end).tolist()

rec = readFile('./reports/rec.csv')

budget = 30000
maxVolume = 100

def getTradeInfo(stock, date):
    historicalData = readFile('./data/historical/{}.csv'.format(stock))
    recentData = historicalData.loc[:date]
    if len(recentData) < 2:
        return ("", 0)
    tradeData = recentData.iloc[[-2]]
    return (str(tradeData.index.values[0])[0:10], tradeData.Close[0])

def getInvestingVolume(price, budget, maxVolume):
    stockVolume = round(budget/price)
    if stockVolume > maxVolume:
        stockVolume = maxVolume
    stockVolume -= stockVolume % 50
    return stockVolume

def isHoliday(tradeDate):
    holidays = pd.read_csv("./data/exceptions/holidays.csv")
    return tradeDate in holidays.Date.values

def isTradable(boughtDate, tradeDate, stock):
    df = readFile('./data/historical/{}.csv'.format(stock))
    print(len(df.loc[tradeDate:boughtDate]))
    return len(df.loc[tradeDate:boughtDate]) >= 3

def appendWaitingList(stock):
    df = pd.read_csv("./reports/waiting_list.csv")
    df.append({'Stock':stock}, ignore_index=True)
    df.to_csv("./reports/waiting_list.csv", index=None)

def sellWaitingList(date, portfolio, budget):
    stocks = pd.read_csv("./reports/waiting_list.csv")
    if len(stocks) > 0:
        print("Selling waiting list...")
        print(stocks)
    for stock in stocks:
        if stock not in portfolio.Stock.values:
            stocks.query('Stock != "{}"'.format(stock), inplace=True)
            continue
        boughtPrice = float(portfolio[portfolio.Stock == stock].Price[0])
        stockVolume = float(portfolio[portfolio.Stock == stock].Volume[0])
        boughtDate = portfolio[portfolio.Stock == stock].Date[0]
        if not isTradable(boughtDate,date,stock):
            continue
        df = readFile('./data/historical/{}.csv'.format(stock))
        tradePrice = df.loc[date].Close[0]
        value = stockVolume * tradePrice
        tradeFee = round(value * 0.0025, 3)
        budget = round(budget + value - tradeFee, 3)
        profit = round((tradePrice - boughtPrice) * stockVolume - 2 * tradeFee, 3)
        trade = {
            "ID": date + "-" + stock,
            "Action": "Sell",
            "Date": date,
            "InvestingAmount": budget,
            "Price": tradePrice,
            "Profit": profit,
            "Stock": stock,
            "TradeFee": tradeFee,
            "Value": value,
            "Volume": stockVolume
        }
        tradeList.append(trade)
        portfolio.query('Stock != "{}"'.format(stock), inplace=True)
        stocks.query('Stock != "{}"'.format(stock), inplace=True)
    stocks.to_csv("./reports/waiting_list.csv", index=None)
    return (portfolio, budget)


def sell(date, sellList, tradeList, portfolio, budget):
    for stock in sellList:
        if stock not in portfolio.Stock.values: 
            continue
        boughtPrice = float(portfolio[portfolio.Stock == stock].Price[0])
        stockVolume = float(portfolio[portfolio.Stock == stock].Volume[0])
        boughtDate = portfolio[portfolio.Stock == stock].Date[0]
        (tradeDate, tradePrice) = getTradeInfo(stock, date)
        if tradeDate == "" and tradePrice == 0:
            print("No trade date {}".format(stock)) 
            continue
        if not isTradable(boughtDate,tradeDate,stock):
            appendWaitingList(stock)
            print("Too soon to sell {} {} {}".format(boughtDate, tradeDate,stock)) 
            continue
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
        print("Selling {} {}".format(stock, tradeDate))
        tradeList.append(trade)
        portfolio.query('Stock != "{}"'.format(stock), inplace=True)
    return (portfolio, budget)

def buy(date, buyList, tradeList, portfolio, budget):
    newPortfolio = []
    for stock in buyList:
        if stock in portfolio.Stock:
            continue
        (tradeDate, tradePrice) = getTradeInfo(stock, date)
        if isHoliday(tradeDate):
            return (portfolio, budget)
        if tradeDate == "" and tradePrice == 0:
            continue
        if isinstance(rec.loc[tradeDate].Sell[0], str):
            print(rec.loc[tradeDate].Sell[0])
        if isinstance(rec.loc[tradeDate].Sell[0], str) and stock in rec.loc[tradeDate].Sell[0]:
            print("Not buy as bad signal {} {} {} {}".format(stock, date, tradeDate, rec.loc[tradeDate].Sell[0]))
            continue
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
    clearFileContent('./reports/portfolio.csv')
    df = pd.read_csv("./reports/waiting_list.csv", index_col="Stock")
    df.iloc[0:0].to_csv('./reports/waiting_list.csv')

clearReports()

for date in dates:
    print(date)
    tradeList = []
    dfTrade = readReport('./reports/trade_report.csv')
    portfolio = readReport('./reports/portfolio.csv')
    sellWaitingList(date, portfolio, budget)
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
