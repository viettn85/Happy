import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from common import readFile, readReport, clearReports

from datetime import datetime
import pandas as pd
import math
pd.options.mode.chained_assignment = None 
start = "2020-01-01"
# start = '2020-03-04'
end = datetime.today().strftime("%Y-%m-%d")
# end = '2020-03-11'
dates = pd.date_range(start, end).tolist()

rec = readFile('./reports/yrb_rec.csv')

days = 3
price = 0

def getBuyPrice(stock, date):
    historicalData = readFile('./data/historical/{}.csv'.format(stock))
    recentData = historicalData.loc[:date]
    if len(recentData) < 1:
        return 0
    tradeData = recentData.iloc[[-1]]
    return tradeData.Close[0]

def isRed(stock, date):
    historicalData = readFile('./data/historical/{}.csv'.format(stock))
    recentData = historicalData.loc[:date]
    if len(recentData) < 1:
        return 0
    tradeData = recentData.iloc[[-1]]
    notRecentData = historicalData.loc[date:]
    if len(notRecentData)==0:
        return True
    previousDay = notRecentData.iloc[[1]]
    # print("{} {} {} {}".format(tradeData.Close[0], tradeData.Open[0], previousDay.Close[0], previousDay.Open[0]))
    return tradeData.Close[0] <= tradeData.Open[0] or previousDay.Close[0] <= previousDay.Open[0]

def getSellPrice(stock, date):
    historicalData = readFile('./data/historical/{}.csv'.format(stock))
    recentData = historicalData.loc[:date]
    if len(recentData) < 2:
        return 0
    tradeData = recentData.iloc[[-1]]
    return tradeData.Close[0]

def isHoliday(tradeDate):
    holidays = pd.read_csv("./data/exceptions/holidays.csv")
    return tradeDate in holidays.Date.values

def sell(date, tradeList, budget):
    portfolio = readReport('./reports/yrb_portfolio.csv')
    sold = []
    for i in range(len(portfolio)):
        portfolio.TD.iloc[i] = portfolio.iloc[i].TD + 1
        if int(portfolio.iloc[i].TD) < days:
            continue
        # print(portfolio)
        boughtPrice = portfolio.Price.iloc[i]
        stock = portfolio.Stock.iloc[i]
        tradePrice = getSellPrice(stock, date)
        volume = portfolio.Volume.iloc[i]
        value = volume * tradePrice
        tradeFee = round(value * 0.0025, 3)
        profit = round((tradePrice - boughtPrice) * volume - 2 * tradeFee, 3)
        date = str(date)[0:10]
        budget = budget - value + tradeFee
        trade = {
            "ID": date + "-" + stock,
            "Action": "Sell",
            "Date": date,
            "Price": tradePrice,
            "Profit": profit,
            "Stock": stock,
            "TradeFee": tradeFee,
            "Value": value,
            "Volume": volume,
            "Budget": budget
        }
        # print("Selling {} {} {}".format(stock, date, portfolio.TD.iloc[i]))
        tradeList.append(trade)
        sold.append(stock)
    for stock in sold:
        portfolio.query('Stock != "{}"'.format(stock), inplace=True)
    portfolio.to_csv('./reports/yrb_portfolio.csv')
    return budget

def getVolume(tradePrice):
    maxBudget = 5000
    stockVolume = round(maxBudget/tradePrice)
    stockVolume -= stockVolume % 50
    return stockVolume

def buy(date, buyList, tradeList, budget):
    # print(pd.Timestamp(str(date)[0:10]).dayofweek)
    # if pd.Timestamp(str(date)[0:10]).dayofweek >= 2:
    #     return budget
    portfolio = readReport('./reports/yrb_portfolio.csv')
    newPortfolio = []
    watchingStocks = ["BID","BVH","CTD","CTG","EIB","FPT","HDB","HPG","MBB","MSN","MWG","PLX","PNJ","POW","REE","ROS","SAB","SBT","SSI","STB","TCB","VCB","VHM","VIC","VJC","VNM","VPB","VRE","ACB","SHB","TPB"] # 
    watchingStocks = ['SCR']
    for stock in buyList:
        # if stock not in watchingStocks:
        #     continue
        if stock in portfolio.Stock:
            continue
        tradePrice = getBuyPrice(stock, date)
        if tradePrice <= 5:
            continue
        if isHoliday(date):
            return budget
        stockVolume = getVolume(tradePrice)
        if stockVolume == 0:
            continue
        if isRed(stock, date):
            continue
        value = stockVolume * tradePrice
        tradeFee = round(value * 0.0025, 3)
        date = str(date)[0:10]
        budget = budget + value + tradeFee
        trade = {
            "ID": date + "-" + stock,
            "Action": "Buy",
            "Date": date,
            "Price": tradePrice,
            "Profit": 0,
            "Stock": stock,
            "TradeFee": tradeFee,
            "Value": value,
            "Volume": stockVolume,
            "Budget": budget
        }
        # print(trade)
        tradeList.append(trade)
        newPortfolio.append({
            "Stock": stock,
            "Date": date,
            "ID": date + "-" + stock,
            "Price": tradePrice,
            "Value": stockVolume * tradePrice,
            "Volume": stockVolume,
            "Sellable": False,
            "TD": 0
        })
        # print("Buying {} {}".format(stock, date))
    if len(newPortfolio) > 0:
        portfolio = portfolio.append(pd.DataFrame(newPortfolio).set_index("ID"))
    portfolio.to_csv('./reports/yrb_portfolio.csv')
    return budget
# START: Only for testing
def clearFileContent(file):
    df = readReport(file)
    df.iloc[0:0].to_csv(file)

def clearReports():
    clearFileContent('./reports/yrb_trade_report.csv')
    clearFileContent('./reports/yrb_portfolio.csv')

clearReports()
budget = 0
vcb = readFile('./data/historical/vcb.csv')
# vcbSub = vcb.loc[end:start]
vcbSub = vcb.loc[end:start]
for i in reversed(range(len(vcbSub))):
    date = vcbSub.index.values[i]
    print(date)
    tradeList = []
    dfTrade = readReport('./reports/yrb_trade_report.csv')
    budget = sell(date, tradeList, budget)
    if isinstance(rec.loc[date].Buy, str):
        budget = buy(date, rec.loc[date].Buy.split('|'), tradeList, budget)
    if len(tradeList) == 0:
        continue
    dfTrade = dfTrade.append(pd.DataFrame(tradeList).set_index("ID"))
    dfTrade.to_csv('./reports/yrb_trade_report.csv')

dfTrade = readReport('./reports/yrb_trade_report.csv')
portfolio = readReport('./reports/yrb_portfolio.csv')

keys = []
values = []
keys.append('Profit')
values.append(dfTrade.Profit.sum())
keys.append('Portfolio')
values.append(len(portfolio))
keys.append('Portfolio Value')
values.append(portfolio.Value.sum())
keys.append('Bad transaction')
values.append(len(dfTrade[(dfTrade.Action == "Sell") & (dfTrade.Profit <= 0)]))
keys.append('Good transaction')
values.append(len(dfTrade[(dfTrade.Action == "Sell") & (dfTrade.Profit > 0)]))
keys.append('Budget')
values.append(dfTrade.Budget.max())

today = datetime.today().strftime("%Y-%m-%d")
dfReport = pd.DataFrame.from_dict({"Keyds": keys, "Values": values})
print(dfReport)


dfReport.to_csv('./reports/test/{}_2019_{}days_sell_{}_YellowBlue_Week.csv'.format(today, days, price))
