
import requests 
from configparser import ConfigParser
import logging
import logging.config
import pandas as pd

from common import getConfigParser

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()
parser = ConfigParser()
parser.read('happy.ini')

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

def getSecurityList(stocks):
    try:
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
        # content = str(requests.get(url=URL, params=PARAMS).content)
        content = "RAS||18817|11^ACB^2380^1960^2170^2150^53590^2160^22360^2170^23730^10^2180^30^2180^1600^2190^18430^2200^37490^250269^2169^2190^2140^0^0^I#12^BID^4130^3590^3860^3840^4085^3845^1686^3850^1211^-10^3850^100^3855^1691^3860^1306^3865^940^162642^3839^3885^3800^6018^66789^I#12^CTG^2235^1945^2090^2105^1916^2110^5952^2115^4387^25^2115^1^2120^8221^2125^10655^2130^9055^435780^2102^2125^2070^24667^107450^I#12^EIB^1655^1445^1550^1560^849^1565^760^1570^571^20^1570^1^1575^2462^1580^3626^1585^2206^47204^1559^1575^1530^0^0^I#12^HDB^2440^2130^2285^2300^2642^2305^1327^2310^1350^25^2310^1^2315^1677^2320^598^2325^643^76045^2287^2320^2255^26825^8387^I#12^MBB^1810^1580^1695^1690^16362^1695^20835^1700^2437^5^1700^54^1705^14704^1710^27667^1715^9597^425066^1695^1710^1680^0^0^I#11^NVB^860^720^790^760^12540^770^12380^780^2390^-10^780^200^790^11320^800^13830^810^1920^312472^780^790^770^0^1000^I#11^SHB^1700^1400^1550^1490^3190^1500^5150^1510^2130^-40^1510^10^1520^3360^1530^9110^1540^11740^547594^1413^1540^1400^80^28710^I#12^STB^1045^912^980^974^6110^975^2936^976^20^-5^975^128^977^1300^978^5850^979^3481^817542^973^985^968^33244^111680^I#12^TCB^2165^1885^2025^2040^2478^2045^7961^2050^1016^25^2050^1^2055^544^2060^10198^2065^11282^234708^2028^2075^1990^185195^185195^I#12^TPB^2335^2035^2185^2120^576^2125^24^2130^688^-35^2150^1^2150^389^2160^1332^2170^3743^7759^2139^2180^2090^0^0^I#12^VCB^8130^7070^7600^7810^86^7820^428^7830^284^230^7830^4^7840^125^7850^1673^7860^343^91515^7712^7900^7580^51932^1999^I#12^VPB^2550^2220^2385^2490^2645^2495^3974^2500^2793^115^2500^2^2505^5631^2510^23650^2515^16198^1002536^2436^2510^2365^205683^25200^I|EOS"
        logger.info(content)
        details = content.split("|")[3]
        securities = details.split("#")
        securityDetails = []
        for security in securities:
            securityDetails.append(extractPrice(security))
        df = pd.DataFrame(securityDetails)
        df.set_index("Stock", inplace=True)
        logger.info(df)
        return df
    except Exception as ex:
        logger.exception(ex)
        logging.debug("Exception when getting stock prices")
        logging.debug(ex)
        return 0

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


def buy(stockList):
    df = getSecurityList(stockList)
    for stock in stockList:
        balance = getAccountBalance()
        price = df.loc[stock].SellPrice1
        volume = getVolumeToBuy(balance, price)
        if volume > 0:
            orderBuy(stock, price, volume)

if __name__ == '__main__':
    getSecurityList(['VCB'])
