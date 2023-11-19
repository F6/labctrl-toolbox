# -*- coding: utf-8 -*-

"""test_api_python_integration.py:
Integration test for Python API library at toolbox.shutter.api.python
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import unittest
import logging
import requests
import json
import os
import time
# third-party libs
from websockets.sync.client import connect
# project packages
from logging_helper import TestingLogFormatter
# package to be tested
from toolbox.shutter.api.python import RemoteShutter

# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)
# configure logger for this module.
lg = logging.getLogger(__name__)

N_TEST_TIMES = 50


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info("Test started")
        cls.shutter = RemoteShutter()

    @classmethod
    def tearDownClass(cls):
        cls.shutter.close()
        lg.info("Test ended.")

    def test_check_restful_availability(self):
        lg.info("Testing check_restful_availability for {} times".format(N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.shutter.check_restful_availability()
            lg.info("Result ({}) for restful availability: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_check_websocket_availability(self):
        target = self.shutter.shutter_list[0]
        lg.info(
            "Testing check_websocket_availability at target shutter {} for {} times".format(target, N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.shutter.check_websocket_availability(target)
            lg.info("Result ({}) for websocket availability: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_restful_commands(self):
        target = self.shutter.shutter_list[0]
        lg.info("Testing RESTful API calls at target shutter {} for {} times".format(
            target, N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.shutter.rest_switch(target)
            lg.info("Result ({}) for calling rest_switch: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_websocket_commands(self):
        target = self.shutter.shutter_list[0]
        lg.info("Testing WebSocket API calls at target shutter {} for {} times".format(
            target, N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.shutter.switch(target, timeout=0)
            lg.info("Result ({}) for calling .switch: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_websocket_commands_noblocking(self):
        target = self.shutter.shutter_list[0]
        lg.info("Testing WebSocket API calls at target shutter {} for {} times, without waiting for synchronize.".format(
            target, N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.shutter.switch(target)
            lg.info("Result ({}) for calling .switch: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))
