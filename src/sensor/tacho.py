from threading import Thread
from configparser import ConfigParser

import RPi.GPIO as GPIO
from gpiozero import DigitalOutputDevice

tachometer_power = DigitalOutputDevice(20)  # pin for 3.3V power supply
tachometer_power.value = 1

TACHOMETER_A_GPIO = 16  # pin for reading tachometer a data
TACHOMETER_B_GPIO = 19  # pin for reading tachometer b data

GPIO.setmode(GPIO.BCM)
GPIO.setup(TACHOMETER_A_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TACHOMETER_B_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SYRINGE_POS_MIN = 3.0  # [ml]
SYRINGE_POS_MAX = 45.0  # [ml]
SYRINGE_TACHOMETER_COUNT_TOTAL = 11000  # [count per 2°] counts in range from MIN to MAX
SYRINGE_PRECISION = 20  # [count per 2°] within targeting positions

config_object = ConfigParser()
config_object.read("config.ini")
current_tachometer_count = config_object.getint("SYRINGE", "position")  # [count per 2°]


def tachometer_a_listener():
    """
    listener for changes on tachometer a pin
    interpreting rectangular incremental signal as global currentTachometerCount
    """
    global current_tachometer_count
    while True:
        GPIO.wait_for_edge(TACHOMETER_A_GPIO, GPIO.RISING)
        if GPIO.input(TACHOMETER_B_GPIO):
            current_tachometer_count += 1
        else:
            current_tachometer_count -= 1


tachometer_a_thread = Thread(target=tachometer_a_listener)  # listen to tachometer a signals in separated thread
tachometer_a_thread.start()


def get_tachometer_data():
    """
    get absolute tachometer count
    """
    return current_tachometer_count  # [count per 2°]


def get_syringe_position():
    """
    get absolute syringe position in ml
    """
    return (SYRINGE_POS_MIN + (SYRINGE_POS_MAX - SYRINGE_POS_MIN)
            * current_tachometer_count / SYRINGE_TACHOMETER_COUNT_TOTAL)  # [ml]


def write_tachometer_position():
    config_object.set("SYRINGE", "position", str(current_tachometer_count))
    with open("config.ini", 'w') as conf:
        config_object.write(conf)
