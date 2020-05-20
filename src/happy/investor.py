import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile
import logging
import logging.config
from datetime import datetime
from mbs import buy

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def investOnRec(date):
    rec = readFile('./reports/rec.csv')
    rec = rec.loc[date:]
    if str(rec.iloc[0].Buy) == 'nan':
        return
    stockList = rec.iloc[0].Buy.split('|')
    buy(stockList)

def checkPattern():
    pass

if __name__ == '__main__':
    date = "2020-05-11"
    investOnRec(date)