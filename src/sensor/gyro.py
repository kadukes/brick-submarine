import logging
import time
from configparser import ConfigParser

import adafruit_icm20x
from adafruit_icm20x import AccelRange, GyroRange
import board

logger = logging.getLogger(__name__)
config_object = ConfigParser()
config_object.read("config.ini")

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

icm.accelerometer_range(AccelRange.RANGE_2G)
icm.gyro_range(GyroRange.RANGE_250_DPS)
icm.gyro_data_rate_divisor(0)
icm.accelerometer_data_rate_divisor(0)
icm.magnetometer_data_rate(1)

ACCEL_CALIBRATION = (0.0, 0.0, 0.0)  # [m/s²]
GYRO_CALIBRATION = (0.0, 0.0, 0.0)  # [rads/s]
angular_velocity = (0.0, 0.0, 0.0)  # [rads/s]
rotation = (0.0, 0.0, 0.0)  # [rads]
acceleration = (0.0, 0.0, 0.0)  # [m/s²]
velocity = (0.0, 0.0, 0.0)  # [m/s]
displacement = (0.0, 0.0, 0.0)  # [m]
magnetometer = (0.0, 0.0, 0.0)  # [µT]
status = 0  # [0 = ok, 1 = error]


def get_angular_velocity():
    return angular_velocity  # [rads/s]


def get_rotation():
    return rotation  # [rads]


def get_acceleration():
    return acceleration  # [m/s²]


def get_velocity():
    return velocity  # [m/s]


def get_displacement():
    return displacement  # [m]


def get_magnetometer():
    return magnetometer  # [µT]


def get_status():
    return status  # [0 = ok, 1 = error]


def get_gyro_data():
    return (
        round_vector(add(icm.acceleration, ACCEL_CALIBRATION)),  # [m/s²]
        round_vector(add(icm.gyro, GYRO_CALIBRATION)),  # [rads/s]
        round_vector(icm.magnetic)  # [µT]
    )


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


def gyro_integrator():
    global status
    global angular_velocity
    global acceleration
    global velocity
    last_velocity = (0.0, 0.0, 0.0)
    global displacement
    global rotation
    global magnetometer
    t_start = time.time_ns()
    pass_filter = 0.90
    last_t = 0.0
    while True:
        t = (time.time_ns() - t_start) / 1000000000
        try:
            acc, gyr, mag = get_gyro_data()
            acc = round_vector(add(mult(1 - pass_filter, acc), mult(pass_filter, acceleration)))
            gyr = round_vector(add(mult(1 - pass_filter, gyr), mult(pass_filter, angular_velocity)))
            velocity = round_vector(add(velocity, mult((t - last_t) / 2, add(acceleration, acc))))
            displacement = round_vector(add(displacement, mult((t - last_t) / 2, add(last_velocity, velocity))))
            rotation = round_vector(add(rotation, mult((t - last_t) / 2, add(angular_velocity, gyr))))
            magnetometer = round_vector(add(mult(1 - pass_filter, mag), mult(pass_filter, magnetometer)))
            last_t = t
            acceleration = acc
            last_velocity = velocity
            angular_velocity = gyr
            status = 0
        except Exception as e:
            logger.critical("Could not read data from gyro sensor. Reason: {}".format(e))
            status = 1


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


def round_vector(x):
    r = ()
    for x_el in x:
        r += (round(x_el, 2),)
    return r
