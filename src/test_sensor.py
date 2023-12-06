from threading import Thread
import logging
from time import sleep

from sensor import adc
from sensor import gyro
from sensor import pressure

logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)


logger.info("Begin testing sensors")
gyro.calibrate()
#gyro.load_calibration()
Thread(target=gyro.gyro_monitor).start() # monitor gyro data

while True:
  logger.info("battery voltage [V]: {}".format(adc.get_battery_voltage()))
  logger.info("displacement [m]: ({}, {}, {})".format(*gyro.get_displacement()))
  sleep(1)
