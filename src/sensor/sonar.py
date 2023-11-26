from threading import Thread
import serial
from time import sleep


SER = serial.Serial(
  port="/dev/serial0",
  baudrate=9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1)


currentMeasuredDistance = 0 # [mm]


def sonarListener():
  global currentMeasuredDistance
  while True:
    if SER.read() == b'\xff':
      data_init = 0xff
      data_buffer = SER.read(3)
      checksum = (data_init + data_buffer[0] + data_buffer[1]) & 0xff
      if data_buffer[2] == checksum:
        currentMeasuredDistance = (data_buffer[0] << 8) + data_buffer[1]

sonarThread = Thread(target=sonarListener) # listen to sonar signals in separated thread
sonarThread.start()


def getSonarData():
  return currentMeasuredDistance # [mm]
