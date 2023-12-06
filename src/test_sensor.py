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

#while True:
#  print("battery voltage [V]: ", adc.getBatteryVoltage(), "\r", end="")
#  print("acceleration [m/s²]: ({:.3f}, {:.3f}, {:.3f})\r".format(gyro.getGyroData()[0][0], gyro.getGyroData()[0][1], gyro.getGyroData()[0][2]), end="")
#  sleep(1)
