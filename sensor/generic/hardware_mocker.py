# -*- coding: utf-8 -*-

"""hardware_config.py:
This module contains a simple hardware mocker that behaves like a real device.
It can be used for testing other modules without actually connected to the device.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231126"

# standard library
import struct
import random
# third party
import cbor2
from cobs import cobs
# this project
from serial_helper import SerialMocker
# this package
from .hardware_config import hardware_config


def response_generator(b: bytes) -> bytes:
    # mocked response according to our protocol
    # naive packetizer,
    # because a serial mocker does not have the framing problems like a real serial port.
    b = cobs.decode(b[:-1])
    p = cbor2.loads(b)
    # parse command and response.
    cmd = p["command"]
    if cmd == "get_data":
        data_name = p["args"]["data"]
        if data_name == "temperature":
            r = {"temperature": 1145 + random.randint(-10, 10)}
        elif data_name == "humidity":
            r = {"humidity": 1919 + random.randint(-10, 10)}
        else:
            r = {"error": "no such data"}
    elif cmd == "get_data_batch":
        data_name = p["args"]["data"]
        data_size = p["args"]["batch_size"]
        if data_name == "temperature":
            r = {"temperature_buffer": struct.pack(
                ">{}H".format(data_size), *list(range(data_size)))}
        elif data_name == "humidity":
            r = {"humidity_buffer": struct.pack(
                ">{}H".format(data_size), *list(range(data_size)))}
        else:
            r = {"error": "no such data"}
    elif cmd == "set_parameter":
        data_name = p["args"]["data"]
        data_value = p["args"]["value"]
        r = {"result": "OK"}
    elif cmd == "start_continuous_mode":
        r = {"result": "OK"}
    elif cmd == "stop_continuous_mode":
        r = {"result": "OK"}
    p = cbor2.dumps(r)
    b = cobs.encode(p) + b'\x00'
    return b


def _burst_message_generator():
    # mock sensor continuous sampling and reporting by burst message mode
    i = 0
    while True:
        yield {"temperature": 1145 + i, "humidity": 1919 + i}
        i = i + 1


bmg = _burst_message_generator()


def burst_message_generator():
    msg = next(bmg)
    p = cbor2.dumps(msg)
    b = cobs.encode(p) + b'\x00'
    return b


ser_cfg = hardware_config.serial
# Replace real serial object of ser_mgr with this mocked one to simulate hardware.
# ser_mgr will open this port when starting so no need to open_by_default.
mocked_ser = SerialMocker(
    ser_cfg.port, baudrate=ser_cfg.baudrate, timeout=ser_cfg.timeout,
    response_generator=response_generator,
    burst_message_generator=burst_message_generator, burst_message_interval=0.1,
    open_by_default=False
)
