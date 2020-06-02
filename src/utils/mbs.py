
import requests 
from configparser import ConfigParser
import logging
import logging.config
import pandas as pd
from datetime import datetime
from common import getConfigParser

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
parser = ConfigParser()
parser.read('happy.ini')
today = datetime.today().strftime("%Y-%m-%d")

def getAccountBalance():
    try:
        URL = parser.get('mbs', 'accountBalance')
        # Params
        pKeyAuthenticate = parser.get('mbs', 'pKeyAuthenticate')
        pMainAccount = parser.get('mbs', 'pMainAccount')
        pAccountCode = parser.get('mbs', 'pAccountCode')
        _ = parser.get('mbs', '_')
        PARAMS = {
                    'pKeyAuthenticate':pKeyAuthenticate,
                    'pMainAccount': pMainAccount,
                    'pAccountCode': pAccountCode,
                    '_': _
                } 
        return int(requests.get(url=URL, params=PARAMS).json()['BuyingPower'])
    except Exception as ex:
        logger.exception(ex)
        logger.debug("Exception when getting account balance")
        logger.debug(ex)
        return 0

def extractPrice(data):
    prices = data.split("^")
    return {
        "Stock": prices[1],
        "Ceiling": int(prices[2]),
        "Floor": int(prices[3]),
        "Reference": int(prices[4]),
        "BuyPrice3": int(prices[5]),
        "BuyVolume3": int(prices[6]),
        "BuyPrice2": int(prices[7]),
        "BuyVolume2": int(prices[8]),
        "BuyPrice1": int(prices[9]),
        "BuyVolume1": int(prices[10]),
        "Change": int(prices[11]),
        "Price": int(prices[12]),
        "CurrentVolume": int(prices[13]),
        "SellPrice1": int(prices[14]),
        "SellVolume1": int(prices[15]),
        "SellPrice2": int(prices[16]),
        "SellVolume2": int(prices[17]),
        "SellPrice3": int(prices[18]),
        "SellVolume3": int(prices[19]),
        "Volume": int(prices[20]),
        "Average": int(prices[21]),
        "High": int(prices[22]),
        "Low": int(prices[23])
    }

def getSecurityList(allStocks):
    noStockPerRequest = 40
    stockList = allStocks.split(',')
    count = int(len(stockList) / noStockPerRequest) + 1
    priceDf = pd.DataFrame([])
    for i in range(count):
        subList = stockList[i * noStockPerRequest: (i+1) * noStockPerRequest]
        if len(subList) == 0:
            continue
        stocks = ','.join(subList)
        df = pd.DataFrame([])
        try:
            logger.info("Requesting to get stock prices")
            logger.info(stocks)
            URL = parser.get('mbs', 'securityList')
            # Params
            pKeyAuthenticate = parser.get('mbs', 'pKeyAuthenticate')
            pMainAccount = parser.get('mbs', 'pMainAccount')
            pTradingCenter = parser.get('mbs', 'pTradingCenter')
            _ = parser.get('mbs', '_')
            PARAMS = {
                        'pKeyAuthenticate':pKeyAuthenticate,
                        'pMainAccount': pMainAccount,
                        'pListShare': stocks,
                        'pTradingCenter': pTradingCenter,
                        '_': _
                    } 
            content = str(requests.get(url=URL, params=PARAMS).content)
            details = content.split("|")[3]
            securities = details.split("#")
            securityDetails = []
            logger.info("Extracting stock prices")
            for security in securities:
                securityDetails.append(extractPrice(security))
            df = pd.DataFrame(securityDetails)
            logger.info("Completed the request to get stock prices")
        except Exception as ex:
            logger.exception(ex)
            logging.debug("Exception when getting stock prices")
            logging.debug(ex)
        priceDf = priceDf.append(df)
    return priceDf

def orderBuy(stock, price, volume):
    try:
        URL = parser.get('mbs', 'newOrder')
        # Params
        pKeyAuthenticate = parser.get('mbs', 'pKeyAuthenticate')
        pMainAccount = parser.get('mbs', 'pMainAccount')
        pTradingCenter = parser.get('mbs', 'pTradingCenter')
        pAccountCode = parser.get('mbs', 'pAccountCode')
        PIN = parser.get('mbs', 'PIN')
        PARAMS = {
                    'pKeyAuthenticate':pKeyAuthenticate,
                    'pMainAccount': pMainAccount,
                    'pTradingCenter': pTradingCenter,
                    'pSide': 'B02',
                    'pAccount': pAccountCode,
                    'pShareCode': stock,
                    'pVolume': volume,
                    'pPrice': price,
                    'pPin': PIN,
                    'pDupOrder': 0,
                    'pOrderBasket': 0,
                    'pNumberOrderBasket': 0,
                    'pRandom': 0.18954746290801205,
                    '_': 1589787007344
                } 
        content = requests.get(url=URL, params=PARAMS).content
        logger.info(content)
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when buying stock ".format(stock))
        logging.debug(ex)
        return 0

def getVolumeToBuy(balance, price):
    parser = getConfigParser()
    maxVolume = int(parser.get('happy', 'max_volume'))
    stockVolume = round(balance/price)
    if stockVolume > stockVolume:
        stockVolume = stockVolume
    stockVolume -= stockVolume % 50
    return stockVolume

def getOrderType(action):
    orderType = ""
    if action.startswith('S'):
        orderType = "Sell"
    if action.startswith('B'):
        orderType = "Buy"
    return orderType

def extractOrder(order):
    details = order.split("^")
    return {
        "Date": today,
        "Time": details[2],
        "Type": getOrderType(details[4]),
        "Stock": details[5],
        "RequestedVol": int(details[6]),
        "MatchedVol": int(details[7]),
        "Price": float(details[8]),
        "Status": details[10],
    }

def getOrders():
    try:
        logger.info("Requesting to get list of orders on {}".format(today))
        URL = parser.get('mbs', 'getOrders')
        # Params
        pKeyAuthenticate = parser.get('mbs', 'pKeyAuthenticate')
        pMainAccount = parser.get('mbs', 'pMainAccount')
        pTradingCenter = parser.get('mbs', 'pTradingCenter')
        _ = parser.get('mbs', '_')
        PARAMS = {
                    'pKeyAuthenticate':pKeyAuthenticate,
                    'pMainAccount': pMainAccount,
                    'pListAccount': '2664538',
                    'pFilterAccount':'',
                    'pFilterStock':'',
                    'pFilterStatus':' ',
                    'pSequence':0,
                    'pPage':1,
                    'pRecordPerPage':50,
                    '_': _
                } 
        content = str(requests.get(url=URL, params=PARAMS).content)
        details = content.split("|")[3]
        orders = details.split("#")
        orderDetails = []
        logger.info("Extracting orders...")
        for order in orders:
            orderDetails.append(extractOrder(order))
        df = pd.DataFrame(orderDetails)
        df = df[['Date', 'Time', 'Type', 'Stock', 'Price', 'MatchedVol', 'RequestedVol', 'Status']]
        logger.info("Complete a request to get list of orders on {}".format(today))
        return df
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when getting stock prices")
        logging.debug(ex)
        return pd.DataFrame([])


def buy(stockList):
    df = getSecurityList(stockList)
    for stock in stockList:
        balance = getAccountBalance()
        price = df.loc[stock].SellPrice1
        volume = getVolumeToBuy(balance, price)
        if volume > 0:
            orderBuy(stock, price, volume)

if __name__ == '__main__':
    print(getSecurityList('VCB,BID,TCB,EIB,VNM,VIC,VHM,DIG'))
    # print(getOrders())
