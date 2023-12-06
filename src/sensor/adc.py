import board
import busio

import adafruit_ads1x15.ads1115 as ads_module
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ads_module.ADS1115(i2c)
chan0 = AnalogIn(ads, ads_module.P0)

# set gain to +/- 2.048 range
ads.gain = 2


def get_battery_voltage():
    return 4 * chan0.voltage, chan0.value  # [V]
