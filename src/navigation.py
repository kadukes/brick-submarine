from time import sleep
from gpiozero import PWMOutputDevice


motorLeft = PWMOutputDevice(22)
motorRight = PWMOutputDevice(27)
motorForward = PWMOutputDevice(18)
motorBackward = PWMOutputDevice(17)

motorLeft.value = 0
motorRight.value = 0
motorForward.value = 0
motorBackward.value = 0


def turn(dir, velocity, duration):
  if dir:
    motorLeft.value = velocity
  else:
    motorRight.value = velocity
  sleep(duration)
  motorLeft.value = 0
  motorRight.value = 0

def forward(dir, velocity, duration):
  if dir:
    motorForward.value = velocity
  else:
    motorBackward.value = velocity
  sleep(duration)
  motorForward.value = 0
  motorBackward.value = 0
