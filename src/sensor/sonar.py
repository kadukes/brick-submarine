import logging
import serial

logger = logging.getLogger(__name__)

SER = serial.Serial(
    port="/dev/serial0",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)

current_measured_distance = 0  # [mm]
status = 0  # [0 = ok, 1 = error]


def sonar_listener():
    global current_measured_distance
    global status
    while True:
        SER.write(0x55)
        if SER.read() == b'\xff':
            data_init = 0xff
            data_buffer = SER.read(3)
            checksum = (data_init + data_buffer[0] + data_buffer[1]) & 0xff
            if data_buffer[2] == checksum:
                current_measured_distance = (data_buffer[0] << 8) + data_buffer[1]
                if current_measured_distance > 0:
                    status = 0
                else:
                    logger.critical("Could not read data from sonar sensor. Reason: Sonar sensor responding with 0.")
                    status = 1
            else:
                logger.critical("Could not read data from sonar sensor. Reason: Sonar sensor checksum mismatch.")
                status = 1


def get_status():
    return status  # [0 = ok, 1 = error]


def get_sonar_data():
    return current_measured_distance  # [mm]
