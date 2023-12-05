# -*- coding: utf-8 -*-

"""test_api_python_integration.py:
Integration test for Python API library at toolbox.sensor.api.python
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

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
from toolbox.sensor.api.python import RemoteSensor

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
        cls.sensor = RemoteSensor()

    @classmethod
    def tearDownClass(cls):
        cls.sensor.close()
        lg.info("Test ended.")

    def test_check_restful_availability(self):
        lg.info("Testing check_restful_availability at sensor for {} times".format(
            N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.sensor.check_restful_availability()
            lg.info("Result ({}) for restful availability: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_check_websocket_availability(self):
        lg.info(
            "Testing check_websocket_availability at sensor for {} times".format(N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.sensor.check_websocket_availability()
            lg.info("Result ({}) for websocket availability: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_restful_commands(self):
        lg.info(
            "Testing RESTful API calls at sensor for {} times".format(N_TEST_TIMES))
        tstart = time.time()
        for i in range(N_TEST_TIMES):
            r = self.sensor.rest_get_data()
            lg.info(
                "Result ({}) for calling rest_get_data: {}".format(i, r))
        tend = time.time()
        telapsed = tend - tstart
        taverage_ms = telapsed / N_TEST_TIMES * 1000
        lg.info("Tstart: {:.6f}s, Tend: {:.6f}s, Telapsed: {:.6f}s, Taverage: {:.6f} ms".format(
            tstart, tend, telapsed, taverage_ms))

    def test_websocket_and_continuous_sampling_mode(self):
        lg.info("Testing WebSocket API for receiveing real time sensor data via continuous sampling mode.")
        r = self.sensor.rest_start_continuous_sampling_mode()
        lg.info("Result for starting continuous sampling mode: {}".format(r))
        time.sleep(5)
        r = self.sensor.rest_stop_continuous_sampling_mode()
        lg.info("Result for stopping continuous sampling mode: {}".format(r))

