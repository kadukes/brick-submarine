from time import sleep
import logging

from sensor import adc

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
        if not last_voltage_monitored < BATTERY_VOLTAGE_CRITICAL and voltage < BATTERY_VOLTAGE_CRITICAL:
            logger.critical("Battery Voltage is at {}".format(voltage))
        elif not last_voltage_monitored < BATTERY_VOLTAGE_LOW and voltage < BATTERY_VOLTAGE_LOW:
            logger.warning("Battery Voltage is at {}".format(voltage))
        elif not last_voltage_monitored < 9.0 and voltage >= BATTERY_VOLTAGE_LOW:
            logger.info("Battery Voltage is at {}".format(voltage))
        last_voltage_monitored = voltage
        sleep(5)
