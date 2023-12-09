import logging
import smbus


logger = logging.getLogger(__name__)

BUS = smbus.SMBus(1)
ADDRESS = 0x28

OUT_MIN = 0x0666  # [counts]
OUT_MAX = 0x3999  # [counts]
P_MIN = 0  # [psi]
P_MAX = 30  # [psi]

filtered_pressure = 0  # [psi]
status = 0  # [0 = ok, 1 = error]


def get_pressure():
    return filtered_pressure  # [psi]


def get_status():
    return status  # [0 = ok, 1 = error]


def read():
    data = BUS.read_i2c_block_data(ADDRESS, 0x00, 4)
    sensor_status = (data[0] >> 6) & 0x03
    pressure = ((data[0] & 0x3f) << 8) | data[1]
    temperature = (data[2] << 3) | ((data[3] >> 5) & 0x07)
    return sensor_status, pressure, temperature


def transform_pressure(raw_pressure_count):
    return round((raw_pressure_count - OUT_MIN) * (P_MAX - P_MIN) / (OUT_MAX - OUT_MIN) + P_MIN, 2)  # [psi]


def transform_temperature(raw_temperature_count):
    return round(raw_temperature_count * 200 / 2047 - 50, 2)  # [°C]


def get_pressure_data():
    sensor_status, pressure, temperature = read()
    return sensor_status, transform_pressure(pressure), transform_temperature(temperature)  # [int], [psi], [°C]


def filter_pressure():
    global filtered_pressure
    global status
    pass_filter = 0.9
    while True:
        try:
            _, p, _ = get_pressure_data()
            filtered_pressure = (1 - pass_filter) * p + pass_filter * filtered_pressure
            status = 0
        except Exception as e:
            logger.critical("Could not read data from pressure sensor. Reason: {}".format(e))
            status = 1
