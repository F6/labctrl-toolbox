# -*- coding: utf-8 -*-

"""hardware_config.py:
This module contains a simple hardware mocker that behaves like a real device.
It can be used for testing other modules without actually connected to the device.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

# standard library
import struct
import random
# third party

# this project
from serial_helper import SerialMocker
# this package
from .hardware_config import hardware_config


def response_generator(b: bytes) -> bytes:
    # mocked response according to our protocol
    # parse command and response.
    if b'MOVEABS' in b:
        return b'OK\r'
    return b''


ser_cfg = hardware_config.serial
# Replace real serial object of ser_mgr with this mocked one to simulate hardware.
# ser_mgr will open this port when starting so no need to open_by_default.
mocked_ser = SerialMocker(
    ser_cfg.port, baudrate=ser_cfg.baudrate, timeout=ser_cfg.timeout,
    response_generator=response_generator,
    open_by_default=False
)