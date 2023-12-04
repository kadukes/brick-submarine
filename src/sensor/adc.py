import board
import busio

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan0 = AnalogIn(ads, ADS.P0)

# set gain to +/- 2.048 range
ads.gain = 2


def get_battery_voltage():
    return 4 * chan0.voltage  # [V]
