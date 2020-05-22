import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import logging
import logging.config
from datetime import datetime

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from common import readFile
from utils import sendEmail


def recommendDaily():
    rec = readFile("./reports/rec.csv")
    today = datetime.today().strftime("%Y-%m-%d")
    buyList = []
    sellList = []
    buyMoreList = []
    try:
        buy = str(rec.loc[today].Buy[0])
        buyMore = str(rec.loc[today].BuyMore[0])
        sell = str(rec.loc[today].Sell[0])
        if isinstance(rec.loc[today].Sell[0], str):
            sellList = rec.loc[today].Sell[0].split('|')
        if isinstance(rec.loc[today].BuyMore[0], str):
            buyMoreList = rec.loc[today].BuyMore[0].split('|')
        if isinstance(rec.loc[today].Buy[0], str):
            buyList = rec.loc[today].Buy[0].split('|')
    except:
        logger.error("No data on {}".format(today))
    shortenedBuyList = []
    for stock in buyList:
        if stock not in sellList:
            shortenedBuyList.append(stock)
    shortenedSellList = []
    portfolio = readFile("./reports/real_portfolio.csv")
    for stock in sellList:
        if stock in portfolio.Stock.values:
            shortenedSellList.append(stock)
    message = """\
Subject: Happy Light House - {}

Today's recommendation:

Stocks to Buy: {}
Stocks to Sell: {}

New UPTREND Stocks: {}

Happy Trading!""".format(today, ", ".join(shortenedBuyList), ", ".join(shortenedSellList), ", ".join(buyMoreList))
    
    return message

if __name__ == '__main__':
    sendEmail(recommendDaily())
