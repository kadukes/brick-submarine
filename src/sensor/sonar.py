import serial

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
<<<<<<< HEAD
        SER.write(0x55)
        if SER.read() == b'\xff':
=======
        if SER.read() == b'\xff':  # TODO: detect timeout
>>>>>>> c7f4e0a4a1d9eb1e3d42816867f0b3570ef67c13
            data_init = 0xff
            data_buffer = SER.read(3)
            checksum = (data_init + data_buffer[0] + data_buffer[1]) & 0xff
            if data_buffer[2] == checksum:
                current_measured_distance = (data_buffer[0] << 8) + data_buffer[1]
                status = 0


def get_status():
    return status  # [0 = ok, 1 = error]


def get_sonar_data():
    return current_measured_distance  # [mm]
