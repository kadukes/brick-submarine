from threading import Thread
from configparser import ConfigParser

import RPi.GPIO as GPIO
from gpiozero import DigitalOutputDevice


tachoPower = DigitalOutputDevice(20) # pin for 3.3V power supply
tachoPower.value = 1

TACHO_A_GPIO = 16 # pin for reading tacho a data
TACHO_B_GPIO = 19 # pin for reading tacho b data

GPIO.setmode(GPIO.BCM)
GPIO.setup(TACHO_A_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TACHO_B_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SYRINGE_POS_MIN = 3.0 # [ml]
SYRINGE_POS_MAX = 45.0 # [ml]
SYRINGE_TACHO_COUNT_TOTAL = 11000 # [count per 2°] counts in range from MIN to MAX
SYRINGE_PRECISION = 20 # [count per 2°] within targeting positions

config_object = ConfigParser()
config_object.read("config.ini")
currentTachoCount = config_object.getint("SYRINGE", "position") # [count per 2°]


def tachoAListener():
  """
  listener for changes on tacho a pin
  interpreting rectangular incremental signal as global currentTachoCount
  """
  global currentTachoCount
  while True:
    GPIO.wait_for_edge(TACHO_A_GPIO, GPIO.RISING)
    if GPIO.input(TACHO_B_GPIO):
      currentTachoCount += 1
    else:
      currentTachoCount -= 1

tachoAThread = Thread(target=tachoAListener) # listen to tacho a signals in separated thread
tachoAThread.start()


def getTachoData():
  """
   get absolute tacho count
  """
  return currentTachoCount # [count per 2°]

def getSyringePosition():
  """
  get absolute syringe position in ml
  """
  return SYRINGE_POS_MIN + (SYRINGE_POS_MAX - SYRINGE_POS_MIN) * currentTachoCount / SYRINGE_TACHO_COUNT_TOTAL # [ml]

def writeTachoPosition():
  config_object.set("SYRINGE", "position", str(currentTachoCount))
  with open("config.ini", 'w') as conf:
    config_object.write(conf)

