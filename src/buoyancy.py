from time import sleep
import logging
from gpiozero import PWMOutputDevice

from sensor import tacho


logger = logging.getLogger(__name__)

motor_up = PWMOutputDevice(12)  # pin for motor control 1
motor_down = PWMOutputDevice(13)  # pin for motor control 2

motor_up.value = 0
motor_down.value = 0


def move(target_position):
    """
    dive or surface by controlling the syringe motor unit

    targetPosition -- [0, SYRINGE_TACHOMETER_COUNT_TOTAL] the target position to move the syringe to
                      (with an error by SYRINGE_BACKLASH)
    """
    if target_position < 0 or target_position > tacho.SYRINGE_TACHOMETER_COUNT_TOTAL:
        logger.error("Cannot move to syringe position {}".format(target_position))
        return

    if target_position < tacho.current_tachometer_count:
        # Experimental result: 18000>> | drift: 200<<
        tacho.current_tachometer_count = (tacho.current_tachometer_count +
                                          int(200 * (tacho.current_tachometer_count - target_position) / 18000))

    while abs(target_position - tacho.current_tachometer_count) > tacho.SYRINGE_PRECISION:
        if target_position < tacho.current_tachometer_count:
            motor_down.value = 0
            motor_up.value = 1
        elif target_position > tacho.current_tachometer_count:
            motor_up.value = 0
            motor_down.value = 1
        sleep(0.1)
    motor_up.value = 0
    motor_down.value = 0
    tacho.write_tachometer_position()  # TODO uncouple this from movement


def move_relative(delta_count):
    """
  WARNING: use this only for debugging!
  move motor relative to current position

  deltaCount -- [int] the relative position from current position to move to
  """
    target_position = tacho.current_tachometer_count + delta_count
    while abs(target_position - tacho.current_tachometer_count) > tacho.SYRINGE_PRECISION:
        if target_position < tacho.current_tachometer_count:
            motor_down.value = 0
            motor_up.value = 1
        elif target_position > tacho.current_tachometer_count:
            motor_up.value = 0
            motor_down.value = 1
        sleep(0.1)
    motor_up.value = 0
    motor_down.value = 0
    tacho.write_tachometer_position()  # TODO uncouple this from movement
