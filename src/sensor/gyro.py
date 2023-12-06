import logging
import time
from configparser import ConfigParser

import adafruit_icm20x
import board

logger = logging.getLogger(__name__)
config_object = ConfigParser()
config_object.read("config.ini")

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

ACCEL_CALIBRATION = (0.0, 0.0, 0.0)  # [m/s²]
GYRO_CALIBRATION = (0.0, 0.0, 0.0)  # [rads/s]
rotation = (0.0, 0.0, 0.0)  # [rads]
velocity = (0.0, 0.0, 0.0)  # [m/s]
displacement = (0.0, 0.0, 0.0)  # [m]


def get_gyro_data():
    return (
        add(icm.acceleration, ACCEL_CALIBRATION),  # [m/s²]
        add(icm.gyro, GYRO_CALIBRATION),  # [rads/s]
        icm.magnetic  # [µT]
    )


def get_rotation():
    return rotation  # [rads]


def get_velocity():
    return velocity  # [m/s]


def get_displacement():
    return displacement  # [m]


def load_calibration():
    global ACCEL_CALIBRATION
    global GYRO_CALIBRATION
    ACCEL_CALIBRATION = (
        config_object.getfloat("ACCELEROMETER", "ax_cal"),
        config_object.getfloat("ACCELEROMETER", "ay_cal"),
        config_object.getfloat("ACCELEROMETER", "az_cal")
    )
    GYRO_CALIBRATION = (
        config_object.getfloat("GYROSCOPE", "gx_cal"),
        config_object.getfloat("GYROSCOPE", "gy_cal"),
        config_object.getfloat("GYROSCOPE", "gz_cal")
    )
    logger.info("Loaded calibration from config file")


def calibrate():
    logger.info("Calibrating accelerometer and gyroscope. Please hold the submarine steady for few seconds...")
    global ACCEL_CALIBRATION
    global GYRO_CALIBRATION
    accel_values = []
    gyro_values = []
    for i in range(200):
        accel, gyro, _ = get_gyro_data()
        accel_values.append(accel)
        gyro_values.append(gyro)
    ACCEL_CALIBRATION = mult(-1 / 200, fold_sum(accel_values))
    GYRO_CALIBRATION = mult(-1 / 200, fold_sum(gyro_values))
    config_object.set("ACCELEROMETER", "ax_cal", str(ACCEL_CALIBRATION[0]))
    config_object.set("ACCELEROMETER", "ay_cal", str(ACCEL_CALIBRATION[1]))
    config_object.set("ACCELEROMETER", "az_cal", str(ACCEL_CALIBRATION[2]))
    config_object.set("GYROSCOPE", "gx_cal", str(GYRO_CALIBRATION[0]))
    config_object.set("GYROSCOPE", "gy_cal", str(GYRO_CALIBRATION[1]))
    config_object.set("GYROSCOPE", "gz_cal", str(GYRO_CALIBRATION[2]))
    with open("config.ini", 'w') as conf:
        config_object.write(conf)
    logger.info("Successfully calibrated accelerometer and gyroscope")


def gyro_monitor():
    last_acc = (0.0, 0.0, 0.0)
    last_gyr = (0.0, 0.0, 0.0)
    global velocity
    last_velocity = (0.0, 0.0, 0.0)
    global displacement
    global rotation
    t_start = time.time_ns()
    pass_filter = 0.95
    pass_precision = 2
    last_t = 0.0
    while True:
        t = (time.time_ns() - t_start) / 1000000000
        acc, gyr, _ = get_gyro_data()
        acc = (round(acc[0], pass_precision), round(acc[1], pass_precision), round(acc[2], pass_precision))
        acc = add(mult(1 - pass_filter, acc), mult(pass_filter, last_acc))
        acc = (round(acc[0], pass_precision), round(acc[1], pass_precision), round(acc[2], pass_precision))
        gyr = (round(gyr[0], pass_precision), round(gyr[1], pass_precision), round(gyr[2], pass_precision))
        gyr = add(mult(1 - pass_filter, gyr), mult(pass_filter, last_gyr))
        gyr = (round(gyr[0], pass_precision), round(gyr[1], pass_precision), round(gyr[2], pass_precision))
        velocity = add(velocity, mult((t - last_t) / 2, add(last_acc, acc)))
        velocity = (round(velocity[0], pass_precision), round(velocity[1], pass_precision), round(velocity[2], pass_precision))
        displacement = add(displacement, mult((t - last_t) / 2, add(last_velocity, velocity)))
        displacement = (round(displacement[0], pass_precision), round(displacement[1], pass_precision), round(displacement[2], pass_precision))
        rotation = add(rotation, mult((t - last_t) / 2, add(last_gyr, gyr)))
        rotation = (round(rotation[0], pass_precision), round(rotation[1], pass_precision), round(rotation[2], pass_precision))
        last_t = t
        last_acc = acc
        last_velocity = velocity
        last_gyr = gyr


def add(x, y):
    r = ()
    for x_el, y_el in zip(x, y):
        r += (x_el + y_el,)
    return r


def fold_sum(x):
    r = (0.0,) * len(x[0])
    for x_el in x:
        r = add(r, x_el)
    return r


def mult(s, x):
    r = ()
    for x_el in x:
        r += (s * x_el,)
    return r
