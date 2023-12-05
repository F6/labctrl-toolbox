# -*- coding: utf-8 -*-

"""test_generic_hardware.py:
unittest toolbox.sensor.tests.test_generic_hardware

This is the unit test for the generic sensor hardware API library.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231123"

# standard library
import unittest
import logging
import time
# third party
# this project
from logging_helper import TestingLogFormatter
# test target
from toolbox.sensor.generic.sensor import ContinuousSamplingMessageHandler
from toolbox.sensor.generic.unit import TemperatureQuantity, SensorTemperatureUnit

# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)
# configure logger for this module.
lg = logging.getLogger(__name__)

class TestHandler(ContinuousSamplingMessageHandler):
    def __init__(self) -> None:
        pass

    def handle_message(self, message: object):
        lg.debug("Message: {}".format(message))


class TestSensorController(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info(
            "Setting up SerialManager of SensorController with a SerialMocker.")
        from toolbox.sensor.generic.sensor import sensor_controller
        cls.sc = sensor_controller
        lg.info("Starting up SensorController")
        cls.sc.start()

    @classmethod
    def tearDownClass(cls):
        lg.info("Shutting down SensorController")
        cls.sc.stop()

    def test_get_temperature(self):
        lg.debug("==== Testing get_temperature ====")
        lg.info("Testing get_temperature for 10 rounds")
        for _ in range(10):
            lg.info("Sending command")
            r = self.sc.get_temperature()
            lg.info("Result: {}".format(r))
            self.assertGreaterEqual(r, 1145-10)
            self.assertLessEqual(r, 1145 + 10)

    def test_get_humidity(self):
        lg.debug("==== Testing test_get_humidity ====")
        lg.info("Testing get_humidity for 10 rounds")
        for _ in range(10):
            lg.info("Sending command")
            r = self.sc.get_humidity()
            lg.info("Result: {}".format(r))
            self.assertGreaterEqual(r, 1919-10)
            self.assertLessEqual(r, 1919 + 10)

    def test_set_parameter(self):
        lg.debug("==== Testing test_set_parameter ====")
        lg.info("Testing set_temperature_sampling_interval")
        lg.info("Sending command")
        r = self.sc.set_temperature_sampling_interval(10)
        lg.info("Result: {}".format(r))
        lg.info("Testing set_humidity_sampling_interval")
        lg.info("Sending command")
        r = self.sc.set_humidity_sampling_interval(10)
        lg.info("Result: {}".format(r))

    def test_get_absolute_temperature(self):
        lg.debug("==== Testing get_absolute_temperature ====")
        lg.info("Sending commands")
        r = self.sc.get_absolute_temperature(unit=SensorTemperatureUnit.KELVIN)
        lg.info("Result: {}".format(r))
        r = self.sc.get_absolute_temperature(
            unit=SensorTemperatureUnit.DEGREE_CELSIUS)
        lg.info("Result: {}".format(r))
        r = self.sc.get_absolute_temperature(
            unit=SensorTemperatureUnit.DEGREE_FAHRENHEIT)
        lg.info("Result: {}".format(r))

    def test_get_temperature_batch(self):
        lg.debug("==== Testing get_temperature_batch ====")
        lg.info("Sending commands")
        r = self.sc.get_temperature_batch(batch_size=100)
        lg.info("Result: {}".format(r))

    def test_continuous_sampling_mode(self):
        lg.debug("==== Testing continuous sampling mode ====")
        lg.info("Sending commands")
        r = self.sc.start_continuous_sampling_mode(
            message_handler=TestHandler())
        lg.info("Result: {}".format(r))
        # mock continuous sampling mode by starting burst mode of serial mocker.
        # you will not get editor hint on this one because ser_mgr.ser is marked as Serial type
        # and the true Serial object does not have test functionalities called burst mode.
        self.sc.ser_mgr.ser.start_burst_message()
        # work in continuous sampling mode for 3 seconds
        time.sleep(3)
        lg.info("Stopping continuous sampling mode.")
        # you will not get editor hint on this one because ser_mgr.ser is marked as Serial type
        # and the true Serial object does not have test functionalities called burst mode.
        self.sc.ser_mgr.ser.stop_burst_message()
        # this is wrong, because messages should only end after sending stop continuous mode 
        # command in this function below, but we have already stopped the messages by
        # calling stop_burst_message. However, we can't hook into this method below to stop
        # the messages at the correct timing because we don't want to introduce additional 
        # artifacts for testing inside production code. So we need to just accept that this
        # cannot be properly tested, unless we use more sophisticated hooks such as raising
        # flags in response_generator and catching the flag changes outside to call
        # stop_burst_message, which is tedious to implement.
        self.sc.stop_continuous_sampling_mode()
        

