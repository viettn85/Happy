from datetime import date
import pandas as pd

from icecream import ic
import logging

LOG_FILENAME = '../logs/happy.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

def scanStock():
    logging.info("Scanning tradable stocks...")
    logging.info("Completed stock scanning")

def run(date):
    try:
        logging.info("Happy running on {}".format(str(date)));
        scanStock();
        
    except Exception as e:
        logging.error(e)
    

if __name__ == '__main__':
    run(str(date.today()))

