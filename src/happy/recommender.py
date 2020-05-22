import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile, readReport
import logging
import logging.config
from datetime import datetime

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def updateTrendingReport(state, stock):
    trendingReport = pd.read_csv("./reports/trending.csv", index_col="Stock")
    # print(state)
    if state == "in":
        row = {
            "Stock": stock,
            "OnTrend": True,
            "Bought": False
        }
        new = pd.DataFrame([row])
        new.set_index('Stock', inplace=True)
        trendingReport = trendingReport.append(new)
    elif state == "out":
        if stock in trendingReport.index.values:
            trendingReport.drop(stock, inplace=True)
    else:
        trendingReport.loc[stock].Bought = True
        # print(trendingReport)
    trendingReport.to_csv("./reports/trending.csv")

def isNotBuyOnTrend(stock):
    trendingReport = pd.read_csv("./reports/trending.csv", index_col="Stock")
    if stock in trendingReport.index.values:
        return not trendingReport.loc[stock].Bought
    return True

def recommendPatterns(date):
    pass

def recommendMA(date):
    logger.info("Started recommendation process on {}".format(date))
    csvFiles = getCsvFiles("./data/historical/")
    # csvFiles = ['KSB.csv'] # ,'BID.csv',,'MWG.csv'
    sell = []
    buy = []
    buyMore = []
    mustSell = pd.read_csv('./data/exceptions/must_sell.csv')
    trends = readReport('./reports/trends.csv')
    for f in csvFiles:
        stock = f[0:3]
        # print(stock)
        df = readFile(("./data/historical/" + f))
        positions = df.index.get_loc(str(date))
        if len(positions) == 0:
            continue
        position = positions[0]
        if date in mustSell.Date.values:
            sell.append(stock)
            df.Recommendation.iloc[position] = "Start Selling"
        positions = df.index.get_loc(str(date))
        if len(positions) == 0:
            continue
        position = positions[0]
        row = df.iloc[position]
        recommendation = ""
        # print(stock)
        # print(df.iloc[position + 1].MA3, df.iloc[position].MA3)
        # print(df.iloc[position + 1].MA8, df.iloc[position].MA8)
        # print(df.iloc[position + 1].MA3_8, df.iloc[position].MA3_8)
        if df.iloc[position].MA3_8 < 0: # c < 0
            if df.iloc[position + 1].MA3_8 >= 0: # p >= 0
                trends = trends.append(pd.DataFrame([{
                    "ID": date + '-' + stock,
                    "Date": date,
                    "Stock": stock,
                    "MA8": df.iloc[position].MA8
                }]).set_index("ID"))
                updateTrendingReport("in", stock)
                buyMore.append(stock)
                if df.iloc[position + 1].MA3 + 0.2 < df.iloc[position].MA3 \
                    and df.iloc[position + 1].MA8 < df.iloc[position].MA8 \
                    and df.iloc[position].MA3_8 <= -0.4:
                    recommendation = "Start Buying"
                    buy.append(stock)
                    updateTrendingReport("bought", stock)
                if df.iloc[position + 1].MA3 >= df.iloc[position].MA3:
                    # print("A")
                    recommendation = "Start Selling"
                    sell.append(stock)
            else: # p < 0
                # print(isNotBuyOnTrend(stock))
                if len(trends[trends.Stock == stock]) == 0:
                    continue
                ma8 = trends[trends.Stock == stock].iloc[-1].MA8
                # print(isNotBuyOnTrend(stock))
                if df.iloc[position + 1].MA3 + 0.2 < df.iloc[position].MA3 \
                    and df.iloc[position + 1].MA8 < df.iloc[position].MA8 \
                    and df.iloc[position].MA3_8 <= -0.4 \
                    and isNotBuyOnTrend(stock):
                    recommendation = "Start Buying"
                    buy.append(stock)
                    updateTrendingReport("bought", stock)
                    # print("B1")
                if ma8 >= df.iloc[position].MA8 or df.iloc[position + 1].MA3 >= df.iloc[position].MA3:
                    # print("B")
                    recommendation = "Start Selling"
                    sell.append(stock)
        else: # c >= 0
            # print(df.iloc[position + 1])
            if df.iloc[position + 1].MA3_8 < 0: # p < 0
                # print("C")
                updateTrendingReport("out", stock)
                recommendation = "Start Selling"
                sell.append(stock)
            else: # p >= 0
                recommendation = "Continue Watching"
        # Update recommendation
        # logger.info((recommendation, df.iloc[position + 1].MA3_8, df.iloc[position].MA3_8))
        # print(recommendation, stock)
        df.Recommendation.iloc[position] = recommendation
        df.to_csv("./data/historical/" + f)
    # Update REC reports
    trends.to_csv('./reports/trends.csv')
    rec = readFile("./reports/rec.csv")
    rec.loc[datetime.strptime(date, "%Y-%m-%d")] = ['|'.join(sell), '|'.join(buy), '|'.join(buyMore)]
    rec.sort_index(ascending=False, inplace=True)
    rec.to_csv('./reports/rec.csv')
    logger.info("Ended recommendation process on {}".format(date))


if __name__ == '__main__':
    date = "2020-05-22"
    date = datetime.today().strftime("%Y-%m-%d")
    recommendMA(date)
