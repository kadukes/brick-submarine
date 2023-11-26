from time import sleep
from gpiozero import PWMOutputDevice

from sensor import tacho


motorUp = PWMOutputDevice(12) # pin for motor control 1
motorDown = PWMOutputDevice(13) # pin for motor control 2

motorUp.value = 0
motorDown.value = 0


def move(targetPosition):
  """
  dive or surface by controlling the syringe motor unit

  targetPosition -- [0, SYRINGE_TACHO_COUNT_TOTAL] the target position to move the syringe to (with an error by SYRINGE_BACKLASH)
  """
  if targetPosition < 0 or targetPosition > tacho.SYRINGE_TACHO_COUNT_TOTAL:
    print("Cannot move to syringe position ", targetPosition)
    return

  if targetPosition < tacho.currentTachoCount:
    # Experimental result: 18000>> | drift: 200<<
    currentTachoCount = tacho.currentTachoCount + int(200 * (tacho.currentTachoCount - targetPosition) / 18000)

  while abs(targetPosition - tacho.currentTachoCount) > tacho.SYRINGE_PRECISION:
    if targetPosition < tacho.currentTachoCount:
      motorDown.value = 0
      motorUp.value = 1
    elif targetPosition > tacho.currentTachoCount:
      motorUp.value = 0
      motorDown.value = 1
    sleep(0.1)
  motorUp.value = 0
  motorDown.value = 0
  tacho.writeTachoPosition() # TODO uncouple this from movement

def move_relative(deltaCount):
  """
  WARNING: use this only for debugging!
  move motor relative to current position

  deltaCount -- [int] the relative position from current position to move to
  """
  targetPosition = tacho.currentTachoCount + deltaCount
  while abs(targetPosition - tacho.currentTachoCount) > tacho.SYRINGE_PRECISION:
    if targetPosition < tacho.currentTachoCount:
      motorDown.value = 0
      motorUp.value = 1
    elif targetPosition > tacho.currentTachoCount:
      motorUp.value = 0
      motorDown.value = 1
    sleep(0.1)
  motorUp.value = 0
  motorDown.value = 0
  tacho.writeTachoPosition() # TODO uncouple this from movement

