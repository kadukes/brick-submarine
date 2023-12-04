import smbus

BUS = smbus.SMBus(1)
ADDRESS = 0x28

OUT_MIN = 0x0666  # [counts]
OUT_MAX = 0x3999  # [counts]
P_MIN = 0  # [psi]
P_MAX = 30  # [psi]


def read():
    data = BUS.read_i2c_block_data(ADDRESS, 0x00, 4)
    status = (data[0] >> 6) & 0x03
    pressure = ((data[0] & 0x3f) << 8) | data[1]
    temperature = (data[2] << 3) | ((data[3] >> 5) & 0x07)
    return status, pressure, temperature


def transform_pressure(raw_pressure_count):
    return (raw_pressure_count - OUT_MIN) * (P_MAX - P_MIN) / (OUT_MAX - OUT_MIN) + P_MIN  # [psi]


def transform_temperature(raw_temperature_count):
    return raw_temperature_count * 200 / 2047 - 50  # [°C]


def get_pressure_data():
    status, pressure, temperature = read()
    return status, transform_pressure(pressure), transform_temperature(temperature)  # [int], [psi], [°C]
