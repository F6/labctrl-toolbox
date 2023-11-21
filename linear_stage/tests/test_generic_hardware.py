# -*- coding: utf-8 -*-

"""test_generic_hardware.py:
unittest toolbox.linear_stage.tests.test_generic_hardware

This is the unit test for the generic linear_stage hardware API library.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

import unittest
import os
import json
import logging

from serial_helper import SerialManager, SerialMocker
from logging_helper import TestingLogFormatter

from toolbox.linear_stage.generic import LinearStageController, LinearStageActionResult
from toolbox.linear_stage.generic.hardware_config import hardware_config
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
        lg.info(
            "Setting up SerialManager of LinearStageController with a SerialMocker.")
        # create LinearStageController that all threads shares according to config.json
        CONFIG_PATH = os.path.join(os.path.dirname(
            __file__), 'test_generic_hardware.config.json')
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
            ser_cfg = cfg["mocked_serial"]

        ser_mgr = SerialManager(
            ser_cfg["port"], baudrate=ser_cfg["baudrate"], timeout=ser_cfg["timeout"])

        # mocked response according to our protocol
        response_map = {
            b"AUTOHOME\r": b"OK\r",
        }

        def r(b: bytes) -> bytes:
            if b'MOVEABS' in b:
                return b'OK\r'
            return b''

        # Replace real serial object of ser_mgr with mocked one
        ser_mgr.ser = SerialMocker(
            ser_cfg["port"], baudrate=ser_cfg["baudrate"], timeout=ser_cfg["timeout"],
            response_map=response_map, response_generator=r
        )

        lg.info("Starting up LinearStageController")
        cls.sc = LinearStageController(ser_mgr, hardware_config)
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
            r = self.sc.move_to_position(10000)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
            lg.info("Moving to -10000 (-10mm)")
            r = self.sc.move_to_position(-10000)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))

    def test_move_to_abs_pos(self):
        lg.debug("==== Testing move_to_absolute_position ====")
        lg.info("Initial position: {}".format(self.sc.position))
        lg.info("Testing move_to_absolute_position back and forth for 10 rounds")
        for _ in range(10):
            lg.info("Moving to 10mm")
            r = self.sc.move_to_absolute_position(
                10.0, StageDisplacementUnit.MILIMETER)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
            lg.info("Moving to -10mm")
            r = self.sc.move_to_absolute_position(
                -10.0, StageDisplacementUnit.MILIMETER)
            lg.info("Result: {}".format(r))
            lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Testing over precision command wanrning")
        lg.info("Moving to 10mm")
        r = self.sc.move_to_absolute_position(
            10.0, StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Moving to 10.0001 mm")
        r = self.sc.move_to_absolute_position(
            10.0001, StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
        lg.info("Moving to -10mm")
        r = self.sc.move_to_absolute_position(-10.0,
                                              StageDisplacementUnit.MILIMETER)
        lg.info("Result: {}".format(r))
        lg.info("Current Position: {}".format(self.sc.position))
