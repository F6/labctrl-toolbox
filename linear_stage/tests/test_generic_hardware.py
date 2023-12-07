# -*- coding: utf-8 -*-

"""test_generic_hardware.py:
unittest toolbox.linear_stage.tests.test_generic_hardware

This is the unit test for the generic linear_stage hardware API library.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

import unittest
import os
import json
import logging

from serial_helper import SerialManager, SerialMocker
from logging_helper import TestingLogFormatter

from toolbox.linear_stage.generic.linear_stage import linear_stage_controller as sc
from toolbox.linear_stage.generic.unit import StageDisplacementUnit
# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)
# configure logger for this module.
lg = logging.getLogger(__name__)


class TestLinearStageController(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info("Importing and Starting LinearStageController")
        cls.sc = sc
        cls.sc.start()

    @classmethod
    def tearDownClass(cls):
        lg.info("Shutting down LinearStageController")
        cls.sc.stop()

    def test_move_to_position(self):
        lg.debug("==== Testing move_to_position ====")
        lg.info("Initial position: {}".format(self.sc.position))
        lg.info("Testing move_to_position back and forth for 10 rounds")
        for _ in range(10):
            lg.info("Moving to 10000 (10mm)")
            r = self.sc.set_position(10000)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
            lg.info("Moving to -10000 (-10mm)")
            r = self.sc.set_position(-10000)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))

    def test_move_to_abs_pos(self):
        lg.debug("==== Testing move_to_absolute_position ====")
        lg.info("Initial position: {}".format(self.sc.position))
        lg.info("Testing move_to_absolute_position back and forth for 10 rounds")
        for _ in range(10):
            lg.info("Moving to 10mm")
            r = self.sc.set_absolute_position(
                10.0, StageDisplacementUnit.MILIMETER)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
            lg.info("Moving to -10mm")
            r = self.sc.set_absolute_position(
                -10.0, StageDisplacementUnit.MILIMETER)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Testing over precision command wanrning")
        lg.info("Moving to 10mm")
        r = self.sc.set_absolute_position(
            10.0, StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Moving to 10.0001 mm")
        r = self.sc.set_absolute_position(
            10.0001, StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Moving to -10mm")
        r = self.sc.set_absolute_position(-10.0,
                                              StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
