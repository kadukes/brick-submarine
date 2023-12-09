from threading import Thread
import logging
from time import sleep

import emergency
from sensor import gyro
from sensor import pressure
from sensor import sonar

logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Begin testing sensors")
gyro.calibrate()
# gyro.load_calibration()

Thread(target=gyro.gyro_integrator).start()  # integrate gyro data
Thread(target=sonar.sonar_listener).start()  # listen to sonar signals

Thread(target=emergency.voltage_monitor).start()  # monitor battery voltage and adc sensor status
Thread(target=emergency.gyro_monitor).start()  # monitor gyro sensor status
Thread(target=emergency.pressure_monitor).start()  # monitor pressure sensor status

while True:
    logger.info("="*100)

    logger.info("Acceleration [m/s²]: ({}, {}, {})".format(*gyro.get_acceleration()))
    logger.info("Velocity [m/s]: ({}, {}, {})".format(*gyro.get_velocity()))
    logger.info("Displacement [m]: ({}, {}, {})".format(*gyro.get_displacement()))
    logger.info("Angular velocity [rads/s]: ({}, {}, {})".format(*gyro.get_angular_velocity()))
    logger.info("Angular rotation [rads]: ({}, {}, {})".format(*gyro.get_rotation()))
    logger.info("Magnetometer [µT]: ({}, {}, {})".format(*gyro.get_magnetometer()))

    logger.info("Pressure [psi]: {}".format(pressure.get_pressure()))
    logger.info("Bottom distance [mm]: {}".format(sonar.get_sonar_data()))

    sleep(1)
