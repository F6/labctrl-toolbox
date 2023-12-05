# -*- coding: utf-8 -*-

"""sensor.py:
This module provides the SensorController class to control a sensor connected via a serial port.
This module uses a temperature sensor as an example.

Concepts:

*Absolute sensor value and logical sensor value*: 

A sensor is a device that measures a real-world physical quantity, such as voltage, temprature, humidity,
distance, velocity, current, etc..
These quantities are in general quite continuous, and are in some units.
Thus, the measured quantity is roughly represented by a floating point number and a unit.
However, floating point numbers have only very limited precision, and are subject to precision loss when converting between units and when doing calculations.

In reality, we cannot measure the physical quantity to arbitrary precision with our simple sensor.
The best precision we can achieve is called the resolution of the apparatus.
Typically, the resolution is limited by some quantizer stage in the measurement system, 
such as the ADC in a circuit.
If our ADC has only 12-bit resolution and has 2.048V reference voltage, then we can only measure the voltage up to a precision level of 0.5 mV.
In that case, there is no reason for us to store our measurement result with a floating point number that introduces errors.
Instead, we can simply use the smallest distinguishable difference in our measurement, called a step, as the unit,
then we can represent all measurements with integers.

    (logical sensor value) * (step size) = (absolute sensor value) * (unit)

Internally, this program uses logical values instead of absolute values to avoid precision loss during calculation and unit conversion.
The absolute values are only calculated and parsed when interacting with external parts.

*Continuous read mode*:

If we are using a sensor as a measurement apparatus, then we instruct the sensor to take a measurement or a series of measurements every time we want a value.
But in many cases a sensor is installed to monitor some state continuously, and polling the sensor value by constantly instructing a measurement is tedious.
In that case, we can use the continuous read mode, which asks the sensor to make measurements every once in a while and report the value continuously to us.
This is an asynchronous approach because we will not be able to know exactly when the sensor will report a value, thus in continuous mode, the sensor values are not returned, and a callback function is required to handle these data.

*CBOR and COBS*:

(See labctrl/serial_helper/COBSFramer documentation.)
Serial port is a low level communication protocol and it does not provide a full-featured data-link layer.
Thus, we need to implement framing and data packaging manually on that data stream the serial port provides.
For a very simple framing and serializing scheme, we can convert all data we need into a JSON string and transmit the string over serial interface, and end each string with a trailing 0x00 byte to indicate boundary.
This works well with slow sensors such as temperature and humidity sensors.
However, for faster sensors such as a camera, encoding binary data into base64 or other string format wastes a lot of bandwidth, memory space and CPU resource.
To efficiently transmit binary data, we can use CBOR over JSON, which supports binary data.
However, data serialized to CBOR can contain any byte including the 0x00 we previously used as a boundary. (In contrast, JSON will never contain 0x00 because it is a string, not binary data.)
Thus, after serializing data into CBOR, we will need a framing algorithm to correctly recognize the boundary of our data.
One efficient algorithm is the COBS algorithm. After encoding our CBOR object with COBS, there will be no 0x00 byte in the encoded result, and we can safely use 0x00 as a boundary marker.
In short, with CBOR and COBS combined, we can construct a standard data-link layer on top of serial port, which is very useful for constructing higher level application layers.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231126"

# std libs
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Any
from threading import Thread
# third party
import cbor2
# this project
from serial_helper import SerialManager, COBSFramer
from .hardware_config import HardwareConfig, TemperatureQuantity, HumidityQuantity, hardware_config
from .unit import sensor_unit_converter, SensorTimeUnit, SensorTemperatureUnit, SensorHumidityUnit
# set up logging
lg = logging.getLogger(__name__)


class SensorActionResult(Enum):
    OK = "OK"
    ERROR_GENERIC = "error_generic"  # one or multiple errors happend
    WARN_NO_ACTION = "warn_no_action"  # no action is performed
    SOFT_LIMIT_EXCEEDED = "soft_limit_exceeded"
    SERIAL_RW_FAILURE = "serial_RW_failure"
    INVALID_ACTION = "invalid_action"
    RESPONSE_VALIDATION_FAILURE = "response_validation_failure"
    DEVICE_ERROR = "device_error"


class ContinuousSamplingMessageHandler(ABC):
    @abstractmethod
    def handle_message(self, message: object):
        pass


class SensorController:
    def __init__(
            self, ser_mgr: SerialManager, config: HardwareConfig) -> None:
        self.ser_mgr = ser_mgr
        self.framer = COBSFramer(self.ser_mgr)
        self.config = config
        self.continuous_sampling_mode_running = False
        self.continuous_sampling_mode_thread: Thread | None = None
        lg.debug("SensorController initialzed.")

    def start(self):
        lg.info("Starting SensorController")
        self.framer.start()
        lg.info("SensorController started.")

    def stop(self):
        lg.info("Gracefully shutting down SensorController")
        self.framer.stop()
        lg.info("SensorController stopped.")

    def command(self, s: dict, timeout: float | None = None):
        lg.debug("Sending command {}".format(s))
        self.framer.send_frame(cbor2.dumps(s), timeout=timeout)
        response = self.framer.receive_frame(timeout=timeout)
        if response is not None:
            result = cbor2.loads(response)
            return result
        else:
            return None

    def get_temperature(self) -> int:
        command = {
            "command": "get_data",
            "args": {
                "data": "temperature"
            }
        }
        r = self.command(command)
        return r['temperature']

    def get_temperature_batch(self, batch_size: int) -> list[int]:
        command = {
            "command": "get_data_batch",
            "args": {
                "data": "temperature",
                "batch_size": batch_size
            }
        }
        r = self.command(command)
        return r['temperature_buffer']

    def get_absolute_temperature(self, unit: SensorTemperatureUnit = SensorTemperatureUnit.KELVIN) -> TemperatureQuantity:
        value = self.get_temperature()
        u = self.config.sensor.temperature.unit_step
        absolute_value = value * u.value
        unit_converted = sensor_unit_converter.convert(
            absolute_value, u.unit, unit)
        return TemperatureQuantity(value=unit_converted, unit=unit)

    def get_humidity(self) -> int:
        command = {
            "command": "get_data",
            "args": {
                "data": "humidity"
            }
        }
        r = self.command(command)
        return r['humidity']

    def get_humidity_batch(self, batch_size: int) -> list[int]:
        command = {
            "command": "get_data_batch",
            "args": {
                "data": "humidity",
                "batch_size": batch_size
            }
        }
        r = self.command(command)
        return r['humidity_buffer']

    def get_absolute_humidity(self, unit: SensorHumidityUnit = SensorHumidityUnit.PERCENT_RELATIVE_HUMIDITY) -> HumidityQuantity:
        """
        [TODO] Implement unit conversion for humidity!
        """
        value = self.get_humidity()
        u = self.config.sensor.humidity.unit_step
        absolute_value = value * u.value
        unit_converted = sensor_unit_converter.convert_humidity(
            absolute_value, u.unit, unit)
        return HumidityQuantity(value=unit_converted, unit=unit)

    def __warn_no_action(self, value):
        lg.warning("Target value is the same as current value: {}".format(value))
        lg.warning(
            "This usually happens when operating beyond the available precision, or system is out of sync. Check docs for more explanation."
        )
        lg.warning("Sending command anyway.")

    def __check_soft_limit_exceeded(self, value: int, minimum: int, maximum: int) -> bool:
        if (value > maximum) or (value < minimum):
            lg.error(
                "Target value exceeds soft limit, target={}, limit=({}, {}).".format(
                    value,
                    minimum,
                    maximum
                ))
            return True
        else:
            return False

    def set_temperature_sampling_interval(self, value: int) -> SensorActionResult:
        result = SensorActionResult.OK
        # Check for soft limit
        param_config = self.config.sensor.temperature.sampling_interval
        if self.__check_soft_limit_exceeded(value, param_config.minimum, param_config.maximum):
            return SensorActionResult.SOFT_LIMIT_EXCEEDED
        # check for precision limit
        if value == param_config.value:
            self.__warn_no_action(value)
            result = SensorActionResult.WARN_NO_ACTION
        # perform the operation
        command = {
            "command": "set_parameter",
            "args": {
                "data": "temperature_sampling_interval",
                "value": value
            }
        }
        r = self.command(command)
        lg.debug("Response from device: {}".format(r))
        if not ('result' in r):
            return SensorActionResult.RESPONSE_VALIDATION_FAILURE
        if r['result'] == "OK":
            param_config.value = value
            return result
        else:
            return SensorActionResult.DEVICE_ERROR

    def set_absolute_temperature_sampling_interval(
            self, interval: float,
            unit: SensorTimeUnit = SensorTimeUnit.MICROSECOND) -> SensorActionResult:
        lg.debug("Setting temperature sampling interval to {} {}".format(
            interval, unit))
        internal_unit = self.config.sensor.temperature.sampling_interval.unit_step.unit
        target_value = sensor_unit_converter.convert(
            interval, unit, internal_unit)
        target_value = int(target_value)
        return self.set_temperature_sampling_interval(value=target_value)

    def set_humidity_sampling_interval(self, value: int) -> SensorActionResult:
        result = SensorActionResult.OK
        # Check for soft limit
        param_config = self.config.sensor.humidity.sampling_interval
        if self.__check_soft_limit_exceeded(value, param_config.minimum, param_config.maximum):
            return SensorActionResult.SOFT_LIMIT_EXCEEDED
        # check for precision limit
        if value == param_config.value:
            self.__warn_no_action(value)
            result = SensorActionResult.WARN_NO_ACTION
        # perform the operation
        command = {
            "command": "set_parameter",
            "args": {
                "data": "humidity_sampling_interval",
                "value": value
            }
        }
        r = self.command(command)
        lg.debug("Response from device: {}".format(r))
        if not ('result' in r):
            return SensorActionResult.RESPONSE_VALIDATION_FAILURE
        if r['result'] == "OK":
            param_config.value = value
            return result
        else:
            return SensorActionResult.DEVICE_ERROR

    def set_absolute_humidity_sampling_interval(
            self, interval: float,
            unit: SensorTimeUnit = SensorTimeUnit.MICROSECOND) -> SensorActionResult:
        lg.debug("Setting humidity sampling interval to {} {}".format(
            interval, unit))
        internal_unit = self.config.sensor.humidity.sampling_interval.unit_step.unit
        target_value = sensor_unit_converter.convert(
            interval, unit, internal_unit)
        target_value = int(target_value)
        return self.set_humidity_sampling_interval(value=target_value)

    def start_continuous_sampling_mode(self, message_handler: ContinuousSamplingMessageHandler) -> SensorActionResult:
        """
        Sends a command to start continuous sampling mode of sensor.
        In this mode, data frames are processed with the message_handler callback function.
        Thus, avoid using command-and-response APIs after continuous mode enabled,
        because the response frame will be processed by the message_handler and are
        probably not received by the command caller, causing a validation error.

        After the sensor confirms the continuous mode, a thread is invoked to process 
        received data frames. The user-defined callback function message_handler
        is called on each received CBOR object (typically a dict).

        NOTE: message_handler is called frequently in another thread, 
        make sure it is thread-safe

        To stop the continuous mode, use stop_continuous_sampling_mode.
        """
        lg.info("Starting continuous sampling mode.")
        if self.continuous_sampling_mode_running:
            lg.error(
                "Continuous Sampling Mode is already running! If restart is intended, stop it first.")
            return SensorActionResult.INVALID_ACTION
        self.continuous_sampling_mode_running = True
        self.continuous_sampling_mode_thread = Thread(
            target=self.__continuous_sampling_mode_task,
            kwargs={"message_handler": message_handler}
        )
        command = {
            "command": "start_continuous_mode",
            "args": {
                "data": ["temperature", "humidity"]
            }
        }
        r = self.command(command)
        lg.debug("Response from device: {}".format(r))
        if not ('result' in r):
            return SensorActionResult.RESPONSE_VALIDATION_FAILURE
        if r['result'] == "OK":
            self.continuous_sampling_mode_thread.start()
            # ======== START TEMPORARY FOR TESTING
            self.ser_mgr.ser.start_burst_message()
            # ======== END TEMPORARY FOR TESTING
            return SensorActionResult.OK
        else:
            return SensorActionResult.DEVICE_ERROR

    def __continuous_sampling_mode_task(self, message_handler: ContinuousSamplingMessageHandler):
        lg.debug("Thread __continuous_sampling_mode_task started.")
        while self.continuous_sampling_mode_running:
            try:
                response = self.framer.receive_frame(timeout=1.0)
                if response:
                    result = cbor2.loads(response)
                    # lg.debug("New report from device: {}".format(result))
                    message_handler.handle_message(result)
            except Exception as e:
                lg.warning(
                    "Unexpected exception while handling continuous sampling mode task.")
                lg.error("Exception caught: {}, {}, {}".format(
                    type(e), e, e.args))
        lg.debug("Thread __continuous_sampling_mode_task ended cleanly.")

    def stop_continuous_sampling_mode(self, wait_for_all_messages_handled: bool = True) -> SensorActionResult:
        """
        Sends a command to device to stop continuous sampling mode,
        then stops the receiving and parsing thread.

        NOTE: This method clears the buffer of framer, this may result in data loss if there's 
        data still in the framer received_packets queue unprocessed after the thread is stopped.
        To avoid this, set wait_for_all_messages_handled = True to wait for all messages to be parsed before ending the thread.
        """
        lg.info(
            "Gracefully shutting down continuous sampling mode threads and clean up messages.")
        if not self.continuous_sampling_mode_running:
            lg.error(
                "Continuous Sampling Mode has not started yet, cannot stop it before start.")
            lg.warning(
                "Sending the stop_continuous_mode command to device anyway, in case this is caused by a state synchronization failure.")
            lg.warning(
                "Corresponding flags and framer buffers will be cleaned as well, be careful!"
            )
        # ======== START TEMPORARY FOR TESTING
        self.ser_mgr.ser.stop_burst_message()
        # ======== END TEMPORARY FOR TESTING
        command = {"command": "stop_continuous_mode"}
        r = self.command(command, timeout=0.1)
        lg.debug("Response from device: {}".format(r))
        # wait for last messages to be processed if desired
        if wait_for_all_messages_handled:
            lg.debug("Waiting for all messages to be handled before shutdown, messages remaining: {}".format(
                self.framer.received_packets.qsize()))
            self.framer.received_packets.join()
        lg.info("Shutting down continuous sampling mode handler thread.")
        self.continuous_sampling_mode_running = False
        if self.continuous_sampling_mode_thread is not None and self.continuous_sampling_mode_thread.is_alive():
            # we can only join existing and running threads.
            self.continuous_sampling_mode_thread.join()
        else:
            lg.warning("Stop is called before continuous sampling initiated!")
        self.framer.clean_up()
        return SensorActionResult.OK


# create SensorController that all threads shares according to config.
serial_config = hardware_config.serial
ser_mgr = SerialManager(
    serial_config.port, baudrate=serial_config.baudrate, timeout=serial_config.timeout)

# ----- FOR TESTING
IS_TESTING = True
if IS_TESTING:
    from .hardware_mocker import mocked_ser
    ser_mgr.ser = mocked_ser
# ===== END FOR TESTING

sensor_controller = SensorController(ser_mgr, hardware_config)
