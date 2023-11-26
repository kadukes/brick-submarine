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

ACCEL_X_CALIBRATION = 0.0 # [m/s²]
ACCEL_Y_CALIBRATION = 0.0 # [m/s²]
ACCEL_Z_CALIBRATION = 0.0 # [m/s²]

GYRO_X_CALIBRATION = 0.0 # [rads/s]
GYRO_Y_CALIBRATION = 0.0 # [rads/s]
GYRO_Z_CALIBRATION = 0.0 # [rads/s]

gyroQueue = queue.Queue() # ([s], [rads/s]³)
accQueue = queue.Queue() # ([s], [m/s²]³)

rotation = (0.0, 0.0, 0.0) # [rads]
velocity = (0.0, 0.0, 0.0) # [m/s]
displacement = (0.0, 0.0, 0.0) # [m]


def getGyroData():
  (accX, accY, accZ) = icm.acceleration
  (gyroX, gyroY, gyroZ) = icm.gyro
  return ((
    accX - ACCEL_X_CALIBRATION, accY - ACCEL_Y_CALIBRATION, accZ - ACCEL_Z_CALIBRATION # [m/s²]
  ),
  (
    gyroX - GYRO_X_CALIBRATION, gyroY - GYRO_Y_CALIBRATION, gyroZ - GYRO_Z_CALIBRATION # [rads/s]
  ),
  icm.magnetic # [µT]
  )

def getRotation():
  return rotation # [rads]

def getVelocity():
  return velocity # [m/s]

def getDisplacement():
  return displacement # [m]

def calibrate():
  global ACCEL_X_CALIBRATION
  global ACCEL_Y_CALIBRATION
  global ACCEL_Z_CALIBRATION
  global GYRO_X_CALIBRATION
  global GYRO_Y_CALIBRATION
  global GYRO_Z_CALIBRATION
  accelXs = []
  accelYs = []
  accelZs = []
  gyroXs = []
  gyroYs = []
  gyroZs = []
  for i in range(200):
    accel, gyro, _ = getGyroData()
    accelXs.append(accel[0])
    accelYs.append(accel[1])
    accelZs.append(accel[2])
    gyroXs.append(gyro[0])
    gyroYs.append(gyro[1])
    gyroZs.append(gyro[2])
  ACCEL_X_CALIBRATION = sum(accelXs) / len(accelXs)
  ACCEL_Y_CALIBRATION = sum(accelYs) / len(accelYs)
  ACCEL_Z_CALIBRATION = sum(accelZs) / len(accelZs)
  GYRO_X_CALIBRATION = sum(gyroXs) / len(gyroXs)
  GYRO_Y_CALIBRATION = sum(gyroYs) / len(gyroYs)
  GYRO_Z_CALIBRATION = sum(gyroZs) / len(gyroZs)

def gyroMonitor():
  sleep(1)
  logger.info("Calibrating accelerometer and gyroscope. Please hold the submarine steady for few seconds...")
  calibrate()
  logger.info("Successfully calibrated accelerometer and gyroscope")

  #gyroIntegratorThread = Thread(target=gyroIntegrator) # integrate gyro data
  #gyroIntegratorThread.start()
  #accIntegratorThread = Thread(target=accIntegrator) # integrate accelerometer data
  #accIntegratorThread.start()
  #queueSizeMonitorThread = Thread(target=queueSizeMonitor) # monitor queue sizes
  #queueSizeMonitorThread.start()

  tStart = time.time_ns()
  with open("accdata.csv", "w") as f:
    while True:
      t = (time.time_ns() - tStart) / 1000000000
      acc, _, _ = getGyroData()
      f.write("{};{};{};{}\n".format(t, acc[0], acc[1], acc[2]))
      #  gyroQueue.put((t, gyro[0], gyro[1], gyro[2]))
      #  accQueue.put((t, acc[0], acc[1], acc[2]))


gyroMonitorThread = Thread(target=gyroMonitor) # monitor gyro data
gyroMonitorThread.start()

def gyroIntegrator():
  global rotation
  lastT = 0.0 # [s]
  lastGyro = (0.0, 0.0, 0.0) # [rads/s]
  while True:
    gyroData = gyroQueue.get()

    rotationX = rotation[0] + (lastGyro[0] + gyroData[1]) / 2 * (gyroData[0] - lastT)
    rotationY = rotation[1] + (lastGyro[1] + gyroData[2]) / 2 * (gyroData[0] - lastT)
    rotationZ = rotation[2] + (lastGyro[2] + gyroData[3]) / 2 * (gyroData[0] - lastT)

    rotation = (rotationX, rotationY, rotationZ)
    lastT = gyroData[0]
    lastGyro = (gyroData[1], gyroData[2], gyroData[3])
    gyroQueue.task_done()

def accIntegrator():
  global velocity
  global displacement
  lastT = 0.0 # [s]
  lastAcc = (0.0, 0.0, 0.0) # [m/s²]
  while True:
    accData = accQueue.get()

    velocityX = velocity[0] + (lastAcc[0] + accData[1]) / 2 * (accData[0] - lastT)
    velocityY = velocity[1] + (lastAcc[1] + accData[2]) / 2 * (accData[0] - lastT)
    velocityZ = velocity[2] + (lastAcc[2] + accData[3]) / 2 * (accData[0] - lastT)
    displacementX = displacement[0] + (velocity[0] + velocityX) / 2 * (accData[0] - lastT)
    displacementY = displacement[1] + (velocity[1] + velocityY) / 2 * (accData[0] - lastT)
    displacementZ = displacement[2] + (velocity[2] + velocityZ) / 2 * (accData[0] - lastT)

    velocity = (velocityX, velocityY, velocityZ)
    displacement = (displacementX, displacementY, displacementZ)
    lastT = accData[0]
    lastAcc = (accData[1], accData[2], accData[3])
    accQueue.task_done()

def queueSizeMonitor():
  while True:
    logger.info("Gyroscope queuesize: {} | Accelerometer queuesize: {}".format(gyroQueue.qsize(), accQueue.qsize()))
    sleep(5)
