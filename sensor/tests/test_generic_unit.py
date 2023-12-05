# -*- coding: utf-8 -*-

"""test_generic_unit.py:
unittest toolbox.sensor.tests.test_generic_unit

This is the unit test for the unit conversion module for sensor units.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231127"

# std libs
import unittest
import logging
import time
import threading
# this project
from logging_helper import TestingLogFormatter
from toolbox.sensor.generic.unit import sensor_unit_converter, SensorHumidityUnit, SensorTemperatureUnit, SensorTimeUnit

# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)
# configure logger for this module.
lg = logging.getLogger(__name__)


class TestGenericUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info("Test starting.")
        cls.uc = sensor_unit_converter

    @classmethod
    def tearDownClass(cls):
        lg.info("End of test")
        for thread in threading.enumerate():
            lg.debug("Currently running threads: {}".format(thread.name))

    def test_unit_conversion(self):
        lg.info("Convert 0 degree celsius to kelvin")
        r = self.uc.convert(0.0, SensorTemperatureUnit.DEGREE_CELSIUS,
                            SensorTemperatureUnit.KELVIN)
        lg.info("Result: {}".format(r))
        assert r == 273.15
        lg.info("Generate conversion table from degree celsius to kelvin")
        for i in range(-270, 500, 20):
            r = self.uc.convert(i, SensorTemperatureUnit.DEGREE_CELSIUS,
                                SensorTemperatureUnit.KELVIN)
            lg.info("{} degC = {} K".format(i, r))
        lg.info("Generate conversion table from degree celsius to fahrenheit")
        for i in range(-270, 500, 20):
            r = self.uc.convert(i, SensorTemperatureUnit.DEGREE_CELSIUS,
                                SensorTemperatureUnit.DEGREE_FAHRENHEIT)
            lg.info("{} degC = {} degF".format(i, r))
        lg.info("Generate conversion table from kelvin to fahrenheit")
        for i in range(0, 500, 20):
            r = self.uc.convert(i, SensorTemperatureUnit.KELVIN,
                                SensorTemperatureUnit.DEGREE_FAHRENHEIT)
            lg.info("{} K = {} degF".format(i, r))
        lg.info("Convert 1ms to s")
        r = self.uc.convert(1.0, SensorTimeUnit.MILISECOND,
                            SensorTimeUnit.SECOND)
        lg.info("Result: {}".format(r))

    def test_unit_conversion_fail(self):
        lg.info("Convert 0 kelvin to nonexistent unit Q")
        try:
            r = self.uc.convert(1, SensorTemperatureUnit.KELVIN,
                                "Q")
            lg.info("Result: {}".format(r))
        except KeyError as e:
            lg.info(
                "Catched exception because no conversion rule available: {}".format(e))
        lg.info("Convert 1ms time to non-time unit kelvin")
        try:
            r = self.uc.convert(1, SensorTimeUnit.MILISECOND,
                                SensorTemperatureUnit.KELVIN)
            lg.info("Result: {}".format(r))
        except KeyError as e:
            lg.info(
                "Catched exception because no conversion rule available: {}".format(e))
