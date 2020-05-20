import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/utils')

from scan import scanNightTime
import logging
import logging.config

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger('nightly-scanner')

date = '2020-05-08'
print("Start nightly scan on {}".format(date))
logger.info("Start nightly scan on {}".format(date))
scanNightTime(date)
