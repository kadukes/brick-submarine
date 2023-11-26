import logging
import sys

FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format=FORMAT, stream=sys.stdout)  # filename='ship.log'
