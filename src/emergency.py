from time import sleep
import logging

from sensor import adc
from sensor import gyro
import buoyancy

logger = logging.getLogger(__name__)

BATTERY_VOLTAGE_LOW = 7.0  # [V]
BATTERY_VOLTAGE_CRITICAL = 6.6  # [V]


def voltage_monitor():
    last_voltage_monitored = 9.0  # [V]
    while True:
        try:
            voltage, _ = adc.get_battery_voltage()
        except Exception as e:
            logger.critical("Could not read data from adc sensor. Reason: {}".format(e))
            break
        if not last_voltage_monitored < BATTERY_VOLTAGE_CRITICAL and voltage < BATTERY_VOLTAGE_CRITICAL:
            logger.critical("Battery Voltage is at {}".format(voltage))
            break
        elif not last_voltage_monitored < BATTERY_VOLTAGE_LOW and voltage < BATTERY_VOLTAGE_LOW:
            logger.warning("Battery Voltage is at {}".format(voltage))
        elif not last_voltage_monitored < 9.0 and voltage >= BATTERY_VOLTAGE_LOW:
            logger.info("Battery Voltage is at {}".format(voltage))
        last_voltage_monitored = voltage
        sleep(10)
    emergency_surface()


def gyro_monitor():
    while True:
        if gyro.get_status() != 0:
            logger.critical("Could not read data from gyro sensor")
            break
        sleep(10)
    emergency_surface()


def emergency_surface():
    logger.critical("Initiating emergency surface...")
    buoyancy.move(0)
