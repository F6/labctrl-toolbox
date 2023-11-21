# -*- coding: utf-8 -*-

"""test_generic_unit.py:
unittest toolbox.linear_stage.tests.test_generic_unit

This is the unit test for the unit conversion module for linear stage units.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import unittest
import os
import json
import logging
# this project
from logging_helper import TestingLogFormatter
from toolbox.linear_stage.generic.unit import *

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
        cls.uc = stage_unit_converter

    @classmethod
    def tearDownClass(cls):
        lg.info("End of test")

    def test_unit_conversion(self):
        lg.info("Convert 1mm to meters")
        r = self.uc.convert(1, StageDisplacementUnit.MILIMETER,
                            StageDisplacementUnit.METER)
        lg.info("Result: {}".format(r))
        assert r == 0.001

    def test_unit_conversion_fail(self):
        lg.info("Convert 1mm to speed unit mm/s")
        try:
            r = self.uc.convert(1, StageDisplacementUnit.MILIMETER,
                                StageVelocityUnit.MILIMETER_PER_SECOND)
            lg.info("Result: {}".format(r))
        except KeyError as e:
            lg.info(
                "Catched exception because no conversion rule available: {}".format(e))
