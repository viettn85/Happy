import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import logging
import logging.config
from icecream import ic
import os
import pandas as pd

from common import getCsvFiles, readRawFile, readFile
from categorization import categorizeCandle
from utils import calculateMAs
from datetime import datetime

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def convert(rawData, historicalData, d3Data):
    logging.info("Started preproceeding process...")
    ic("Started preproceeding process...")
    csvFiles = getCsvFiles(rawData)
    # csvFiles = ['BID.csv','VRE.csv']
    converted = readFile('./reports/converted.csv')
    convertedList = list(converted.Stock)
    new = []
    for f in csvFiles:
        if f in convertedList:
            continue
        df = readRawFile((rawData + f))
        if not {'date', 'close', "high", "low", "open", "volume"}.issubset(df.columns):
            os.remove(rawData + f)
            ic("Removed", f)
            logging.info("Removed wrong format data of {}".format(f))
            continue
        ic("Converting {}".format(f))
        df.rename(columns={'date': 'Date', 'close': 'Close', 'open': 'Open', 'high': 'High', 'low': 'Low', 'volume': 'Volume'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index("Date", inplace=True)
        calculateMAs(df)
        df["Change"] = round(abs(df.Close - df.Open)/df.Open * 100, 2)
        df = df[["Close", "Open", "High", "Low", "Change", "Volume", "MA3", "MA8", "MA20", "MA3_8", "MA3_20", "MA8_20"]]
        # Generate ascending data for D3
        # df.sort_index(ascending=True, inplace=True)
        df.to_csv(d3Data + f)
        # Generate decending data
        df["Short"] = False
        df["Long"] = False
        df["Category"] = ""
        df["Recommendation"] = ""
        df["Action"] = ""
        for i in range(len(df)):
            categorizeCandle(df, i)
        df.sort_index(ascending=False, inplace=True)
        df.to_csv(historicalData + f)
        new.append(f)
    dates = [datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")] * len(new)
    newConverted = pd.DataFrame.from_dict({
        'Date': dates,
        'Stock': new
    })
    newConverted.set_index('Date', inplace=True)
    converted = converted.append(newConverted)
    converted.to_csv('./reports/converted.csv')
    logging.info("Completed preproceeding process...")
    ic("Completed preproceeding process...")

def etl():
    logger.info("Started ETL processing...")
    convert("./data/raw_data/", "./data/historical/", "./data/d3/")
    logger.info("Started ETL processing...")

etl()