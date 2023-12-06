import logging
import time
from configparser import ConfigParser

import board
import adafruit_icm20x

logger = logging.getLogger(__name__)

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

config_object = ConfigParser()
config_object.read("config.ini")

ACCEL_X_CALIBRATION = 0.0  # [m/s²]
ACCEL_Y_CALIBRATION = 0.0  # [m/s²]
ACCEL_Z_CALIBRATION = 0.0  # [m/s²]

GYRO_X_CALIBRATION = 0.0  # [rads/s]
GYRO_Y_CALIBRATION = 0.0  # [rads/s]
GYRO_Z_CALIBRATION = 0.0  # [rads/s]

rotation = (0.0, 0.0, 0.0)  # [rads]
velocity = (0.0, 0.0, 0.0)  # [m/s]
displacement = (0.0, 0.0, 0.0)  # [m]


def get_gyro_data():
    (accX, accY, accZ) = icm.acceleration
    (gyroX, gyroY, gyroZ) = icm.gyro
    return ((accX - ACCEL_X_CALIBRATION, accY - ACCEL_Y_CALIBRATION, accZ - ACCEL_Z_CALIBRATION),  # [m/s²]
            (gyroX - GYRO_X_CALIBRATION, gyroY - GYRO_Y_CALIBRATION, gyroZ - GYRO_Z_CALIBRATION),  # [rads/s]
            icm.magnetic)  # [µT]


def get_rotation():
    return rotation  # [rads]


def get_velocity():
    return velocity  # [m/s]


def get_displacement():
    return displacement  # [m]


def load_calibration():
    global ACCEL_X_CALIBRATION
    global ACCEL_Y_CALIBRATION
    global ACCEL_Z_CALIBRATION
    global GYRO_X_CALIBRATION
    global GYRO_Y_CALIBRATION
    global GYRO_Z_CALIBRATION
    ACCEL_X_CALIBRATION = config_object.getfloat("ACCELEROMETER", "ax_cal")
    ACCEL_Y_CALIBRATION = config_object.getfloat("ACCELEROMETER", "ay_cal")
    ACCEL_Z_CALIBRATION = config_object.getfloat("ACCELEROMETER", "az_cal")
    GYRO_X_CALIBRATION = config_object.getfloat("GYROSCOPE", "gx_cal")
    GYRO_Y_CALIBRATION = config_object.getfloat("GYROSCOPE", "gy_cal")
    GYRO_Z_CALIBRATION = config_object.getfloat("GYROSCOPE", "gz_cal")
    logger.info("Loaded calibration from config file")


def calibrate():
    logger.info("Calibrating accelerometer and gyroscope. Please hold the submarine steady for few seconds...")
    global ACCEL_X_CALIBRATION
    global ACCEL_Y_CALIBRATION
    global ACCEL_Z_CALIBRATION
    global GYRO_X_CALIBRATION
    global GYRO_Y_CALIBRATION
    global GYRO_Z_CALIBRATION
    accel_xs = []
    accel_ys = []
    accel_zs = []
    gyro_xs = []
    gyro_ys = []
    gyro_zs = []
    for i in range(200):
        accel, gyro, _ = get_gyro_data()
        accel_xs.append(accel[0])
        accel_ys.append(accel[1])
        accel_zs.append(accel[2])
        gyro_xs.append(gyro[0])
        gyro_ys.append(gyro[1])
        gyro_zs.append(gyro[2])
    ACCEL_X_CALIBRATION = sum(accel_xs) / len(accel_xs)
    ACCEL_Y_CALIBRATION = sum(accel_ys) / len(accel_ys)
    ACCEL_Z_CALIBRATION = sum(accel_zs) / len(accel_zs)
    GYRO_X_CALIBRATION = sum(gyro_xs) / len(gyro_xs)
    GYRO_Y_CALIBRATION = sum(gyro_ys) / len(gyro_ys)
    GYRO_Z_CALIBRATION = sum(gyro_zs) / len(gyro_zs)
    config_object.set("ACCELEROMETER", "ax_cal", str(ACCEL_X_CALIBRATION))
    config_object.set("ACCELEROMETER", "ay_cal", str(ACCEL_Y_CALIBRATION))
    config_object.set("ACCELEROMETER", "az_cal", str(ACCEL_Z_CALIBRATION))
    config_object.set("GYROSCOPE", "gx_cal", str(GYRO_X_CALIBRATION))
    config_object.set("GYROSCOPE", "gy_cal", str(GYRO_Y_CALIBRATION))
    config_object.set("GYROSCOPE", "gz_cal", str(GYRO_Z_CALIBRATION))
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
            acc_filtered = (
              (1 - pass_filter) * acc[0] + pass_filter * acc_filtered[0],
              (1 - pass_filter) * acc[1] + pass_filter * acc_filtered[1],
              (1 - pass_filter) * acc[2] + pass_filter * acc_filtered[2]
            )

            vel = (
              vel[0] + (last_acc[0] + acc[0]) / 2 * (t - last_t),
              vel[1] + (last_acc[1] + acc[1]) / 2 * (t - last_t),
              vel[2] + (last_acc[2] + acc[2]) / 2 * (t - last_t)
            )
            vel_filtered = (
              vel_filtered[0] + (last_acc_filtered[0] + acc_filtered[0]) / 2 * (t - last_t),
              vel_filtered[1] + (last_acc_filtered[1] + acc_filtered[1]) / 2 * (t - last_t),
              vel_filtered[2] + (last_acc_filtered[2] + acc_filtered[2]) / 2 * (t - last_t)
            )

            dis = (
              dis[0] + (last_vel[0] + vel[0]) / 2 * (t - last_t),
              dis[1] + (last_vel[1] + vel[1]) / 2 * (t - last_t),
              dis[2] + (last_vel[2] + vel[2]) / 2 * (t - last_t)
            )
            dis_filtered = (
              dis_filtered[0] + (last_vel_filtered[0] + vel_filtered[0]) / 2 * (t - last_t),
              dis_filtered[1] + (last_vel_filtered[1] + vel_filtered[1]) / 2 * (t - last_t),
              dis_filtered[2] + (last_vel_filtered[2] + vel_filtered[2]) / 2 * (t - last_t)
            )

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
