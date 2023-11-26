import sys
from time import sleep
import logging

import buoyancy
from sensor import tacho
from sensor import pressure
from sensor import sonar

import navigation
from sensor import gyro

import power
from sensor import adc


FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format=FORMAT, stream=sys.stdout) #, filename='ship.log')
