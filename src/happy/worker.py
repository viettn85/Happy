import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import logging
import logging.config
from datetime import datetime

from configparser import ConfigParser
from daily_update import Crawl
from common import getCsvFiles

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def updateDaily(date):
    logger.info("Started updating on {}".format(date))
    csvFiles = getCsvFiles("./data/historical/")
    # csvFiles = ['VCB.csv']
    for i, csv in enumerate(csvFiles):
        try:
            logger.info((i, csv[0:3]))
            Crawl(csv[0:3], './data/historical/').run()
        except Exception as e:
            logger.error(e)
    logger.info("Ended updating on {}".format(date))

def copyHistoricalData(date):
    # Copy historical data to daily data
    logger.info("Started copying historical data on {}".format(date))
    import os
    import shutil
    src_files = os.listdir("./data/historical")
    for file_name in src_files:
        full_file_name = os.path.join("./data/historical", file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, "./data/daily")
    logger.info("Ended copying historical data on {}".format(date))

today = datetime.today().strftime("%Y-%m-%d")
updateDaily(today)
copyHistoricalData(today)