from threading import Thread
from time import sleep
import logging

from sensor import adc


BATTERY_VOLTAGE_LOW = 7.0 # [V]
BATTERY_VOLTAGE_CRITICAL = 6.6 # [V]
lastVoltageMonitored = 9.0 # [V]


def voltageMonitor():
  global lastVoltageMonitored
  while True:
    voltage = adc.getBatteryVoltage()
    if not lastVoltageMonitored < BATTERY_VOLTAGE_CRITICAL and voltage < BATTERY_VOLTAGE_CRITICAL:
      logging.critical("Battery Voltage is at {:.2f}. Initiating emergency protocol...".format(voltage))
    elif not lastVoltageMonitored < BATTERY_VOLTAGE_LOW and voltage < BATTERY_VOLTAGE_LOW:
      logging.warning("Battery Voltage is at {:.2f}".format(voltage))
    elif not lastVoltageMonitored > BATTERY_VOLTAGE_LOW and voltage >= BATTERY_VOLTAGE_LOW:
      logging.info("Battery Voltage is at {:.2f}".format(voltage))
    lastVoltageMonitored = voltage
    sleep(5)

voltageMonitorThread = Thread(target=voltageMonitor) # monitor battery voltage
voltageMonitorThread.start()

