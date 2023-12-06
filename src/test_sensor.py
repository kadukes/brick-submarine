from threading import Thread
import logging
from time import sleep

from sensor import adc
from sensor import gyro
from sensor import pressure
from sensor import sonar

logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Begin testing sensors")
gyro.calibrate()
# gyro.load_calibration()
Thread(target=gyro.gyro_monitor).start()  # monitor gyro data

while True:
    try:
        logger.info("Battery voltage [V]: {}; Value: {}".format(*adc.get_battery_voltage()))
    except Exception as e:
        logger.error("Could not read adc sensor! Reason: {}".format(e))

    try:
        logger.info("Acceleration [m/s²]: ({}, {}, {})".format(*gyro.get_gyro_data()[0]))
        logger.info("Velocity [m/s]: ({}, {}, {})".format(*gyro.get_velocity()))
        logger.info("Displacement [m]: ({}, {}, {})".format(*gyro.get_displacement()))
        logger.info("Angular velocity [rads/s]: ({}, {}, {})".format(*gyro.get_gyro_data()[1]))
        logger.info("Angular rotation [rads]: ({}, {}, {})".format(*gyro.get_rotation()))
        logger.info("Magnetometer [µT]: ({}, {}, {})".format(*gyro.get_gyro_data()[2]))
    except Exception as e:
        logger.error("Could not read gyro sensor! Reason: {}".format(e))

    try:
        logger.info("Status: {}; Pressure [psi]: {}; Temperature [°C]: {}".format(*pressure.get_pressure_data()))
    except Exception as e:
        logger.error("Could not read pressure sensor! Reason: {}".format(e))

    try:
        logger.info("Bottom distance [mm]: {}".format(sonar.get_sonar_data()))
    except Exception as e:
        logger.error("Could not read pressure sensor! Reason: {}".format(e))
    sleep(1)
