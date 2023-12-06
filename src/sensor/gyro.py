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
    acc_filtered = (0.0, 0.0, 0.0)
    last_acc_filtered = (0.0, 0.0, 0.0)
    last_vel = (0.0, 0.0, 0.0)
    last_vel_filtered = (0.0, 0.0, 0.0)
    t_start = time.time_ns()
    pass_filter = 0.8
    last_t = 0.0
    with open("accdata_raw.csv", "w") as f:
        f.write("time;acc_x;acc_y;acc_z;acc_x_filtered;acc_y_filtered;acc_z_filtered;")
        f.write("vel_x;vel_y;vel_z;vel_x_filtered;vel_y_filtered;vel_z_filtered;")
        f.write("dis_x;dis_y;dis_z;dis_x_filtered;dis_y_filtered;dis_z_filtered\n")
        while True:
            t = (time.time_ns() - t_start) / 1000000000
            acc, _, _ = get_gyro_data()
            acc_filtered = add(mult(1 - pass_filter, acc), mult(pass_filter, acc_filtered))

            vel = add(vel, mult((t - last_t) / 2, add(last_acc, acc)))
            vel_filtered = add(vel_filtered, mult((t - last_t) / 2, add(last_acc_filtered, acc_filtered)))

            dis = add(dis, mult((t - last_t) / 2, add(last_vel, vel)))
            dis_filtered = add(dis_filtered, mult((t - last_t) / 2, add(last_vel_filtered, vel_filtered)))

            last_t = t
            last_acc = acc
            last_acc_filtered = acc_filtered
            last_vel = vel
            last_vel_filtered = vel_filtered
            f.write("{};{:.2f};{:.2f};{:.2f};".format(t, acc[0], acc[1], acc[2]))
            f.write("{:.2f};{:.2f};{:.2f};".format(acc_filtered[0], acc_filtered[1], acc_filtered[2]))
            f.write("{:.2f};{:.2f};{:.2f};".format(vel[0], vel[1], vel[2]))
            f.write("{:.2f};{:.2f};{:.2f};".format(vel_filtered[0], vel_filtered[1], vel_filtered[2]))
            f.write("{:.2f};{:.2f};{:.2f};".format(dis[0], dis[1], dis[2]))
            f.write("{:.2f};{:.2f};{:.2f}\n".format(dis_filtered[0], dis_filtered[1], dis_filtered[2]))


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
