import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile, readReport
import logging
import logging.config
from datetime import datetime
from mbs import getOrders
from utils import sendEmail

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")

def updatePortfolio(df):
    logger.info("Started updating portfolio on {}".format(today))
    portfolio = readReport('./reports/real_portfolio.csv')
    orders = []
    for i in range(len(df)):
        order = df.iloc[i]
        orders.append({
            'ID': order.Date + "-" + order.Stock,
            'Date': order.Date,
            'Type': order.Type,
            'Price': order.Price,
            'Sellable': False,
            'Stock': order.Stock,
            'Value':float(order.Price * order.MatchedVol),
            'Volume': order.MatchedVol
        })
    newPortfolio = pd.DataFrame(orders)
    newPortfolio.set_index("ID", inplace=True)
    portfolio = portfolio.append(newPortfolio)
    portfolio.to_csv("./reports/real_portfolio.csv")
    logger.info("Ended updating portfolio on {}".format(today))

def generateMessage():
    portfolio = readReport('./reports/real_portfolio.csv')
    orders = []
    for i in range(len(portfolio)):
        order = portfolio.iloc[i]
        # print(order)
        orders.append('{} {} {} with price {} value {}'\
            .format(order.Type, order.Volume, order.Stock, order.Price, order.Price * order.Volume))
    details = "\n".join(orders)
    
    message = """\
Subject: Orders - {}

Today's orders:

{}

Happy Trading!""".format(today, details)
    sendEmail(message)

if __name__ == '__main__':
    df = getOrders()
    updatePortfolio(df)
    generateMessage()
