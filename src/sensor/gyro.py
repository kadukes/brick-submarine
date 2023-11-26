from threading import Thread
import queue
from time import sleep
import time
import logging

import board
import adafruit_icm20x

logger = logging.getLogger(__name__)

i2c = board.I2C()
icm = adafruit_icm20x.ICM20948(i2c)

ACCEL_X_CALIBRATION = 0.0  # [m/s²]
ACCEL_Y_CALIBRATION = 0.0  # [m/s²]
ACCEL_Z_CALIBRATION = 0.0  # [m/s²]

GYRO_X_CALIBRATION = 0.0  # [rads/s]
GYRO_Y_CALIBRATION = 0.0  # [rads/s]
GYRO_Z_CALIBRATION = 0.0  # [rads/s]

gyroQueue = queue.Queue()  # ([s], [rads/s]³)
accQueue = queue.Queue()  # ([s], [m/s²]³)

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


def calibrate():
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


def gyro_monitor():
    sleep(1)
    logger.info("Calibrating accelerometer and gyroscope. Please hold the submarine steady for few seconds...")
    calibrate()
    logger.info("Successfully calibrated accelerometer and gyroscope")

    # gyroIntegratorThread = Thread(target=gyroIntegrator) # integrate gyro data
    # gyroIntegratorThread.start()
    # accIntegratorThread = Thread(target=accIntegrator) # integrate accelerometer data
    # accIntegratorThread.start()
    # queueSizeMonitorThread = Thread(target=queueSizeMonitor) # monitor queue sizes
    # queueSizeMonitorThread.start()

    t_start = time.time_ns()
    with open("acc_data.csv", "w") as f:
        while True:
            t = (time.time_ns() - t_start) / 1000000000
            acc, _, _ = get_gyro_data()
            f.write("{};{};{};{}\n".format(t, acc[0], acc[1], acc[2]))
            #  gyroQueue.put((t, gyro[0], gyro[1], gyro[2]))
            #  accQueue.put((t, acc[0], acc[1], acc[2]))


gyroMonitorThread = Thread(target=gyro_monitor)  # monitor gyro data
gyroMonitorThread.start()


def gyro_integrator():
    global rotation
    last_t = 0.0  # [s]
    last_gyro = (0.0, 0.0, 0.0)  # [rads/s]
    while True:
        gyro_data = gyroQueue.get()

        rotation_x = rotation[0] + (last_gyro[0] + gyro_data[1]) / 2 * (gyro_data[0] - last_t)
        rotation_y = rotation[1] + (last_gyro[1] + gyro_data[2]) / 2 * (gyro_data[0] - last_t)
        rotation_z = rotation[2] + (last_gyro[2] + gyro_data[3]) / 2 * (gyro_data[0] - last_t)

        rotation = (rotation_x, rotation_y, rotation_z)
        last_t = gyro_data[0]
        last_gyro = (gyro_data[1], gyro_data[2], gyro_data[3])
        gyroQueue.task_done()


def acc_integrator():
    global velocity
    global displacement
    last_t = 0.0  # [s]
    last_acc = (0.0, 0.0, 0.0)  # [m/s²]
    while True:
        acc_data = accQueue.get()

        velocity_x = velocity[0] + (last_acc[0] + acc_data[1]) / 2 * (acc_data[0] - last_t)
        velocity_y = velocity[1] + (last_acc[1] + acc_data[2]) / 2 * (acc_data[0] - last_t)
        velocity_z = velocity[2] + (last_acc[2] + acc_data[3]) / 2 * (acc_data[0] - last_t)
        displacement_x = displacement[0] + (velocity[0] + velocity_x) / 2 * (acc_data[0] - last_t)
        displacement_y = displacement[1] + (velocity[1] + velocity_y) / 2 * (acc_data[0] - last_t)
        displacement_z = displacement[2] + (velocity[2] + velocity_z) / 2 * (acc_data[0] - last_t)

        velocity = (velocity_x, velocity_y, velocity_z)
        displacement = (displacement_x, displacement_y, displacement_z)
        last_t = acc_data[0]
        last_acc = (acc_data[1], acc_data[2], acc_data[3])
        accQueue.task_done()


def queue_size_monitor():
    while True:
        logger.info("Gyroscope queue size: {} | Accelerometer queue size: {}"
                    .format(gyroQueue.qsize(), accQueue.qsize()))
        sleep(5)
