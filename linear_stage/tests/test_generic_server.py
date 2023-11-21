# -*- coding: utf-8 -*-

"""test_generic_server.py:
Tests remote APIs of the server.
Before running this test, first make sure the server is running.
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


# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)
# configure logger for this module.
lg = logging.getLogger(__name__)


class TestGenericServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info("Reading config file.")
        CONFIG_PATH = os.path.join(os.path.dirname(
            __file__), 'test_generic_server.config.json')
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
        lg.info("Authenticating client.")
        restful_config = cfg["restful"]
        cls.restful_endpoint = restful_config["protocol"] + restful_config["host"] + \
            ":" + str(restful_config["port"]) + restful_config["endpoint"]
        websocket_config = cfg["websocket"]
        cls.websocket_endpoint = websocket_config["protocol"] + websocket_config["host"] + \
            ":" + str(websocket_config["port"]) + websocket_config["endpoint"]
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": cfg["authentication"]["username"],
            "password": cfg["authentication"]["password"]
        }
        response = requests.post(cls.restful_endpoint + "token",
                                 headers=headers,
                                 data=data)
        result = json.loads(response.content.decode())
        assert "access_token" in result
        lg.info("Successfully logged in, token type: {}".format(
            result["token_type"]))
        cls.auth = result
        cls.auth_str = cls.auth["token_type"] + " " + cls.auth["access_token"]

    @classmethod
    def tearDownClass(cls):
        lg.info("Test ended.")

    def test_get_resource_names(self):
        lg.info("Requesting to get a list of available resources from server")
        response = requests.get(self.restful_endpoint)
        lg.info("Got response: {} with header: {}".format(
            response.status_code, response.headers))
        result = json.loads(response.content.decode())
        lg.info("Result: {}".format(result))
        assert "resources" in result
        assert "position" in result["resources"]
        assert "velocity" in result["resources"]

    def test_get_position(self):
        lg.info("Requesting to get current position from server")
        headers = {
            "accept": "application/json",
            "Authorization": self.auth_str
        }
        response = requests.get(self.restful_endpoint + "position", headers=headers)
        lg.info("Got response: {} with header: {}".format(
            response.status_code, response.headers))
        result = json.loads(response.content.decode())
        lg.info("Result: {}".format(result))
        assert "value" in result

    def test_set_position(self):
        lg.info("Requesting to move stage to position 114514")
        headers = {
            "accept": "application/json",
            "Authorization": self.auth_str,
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "value": 114514
        }).encode()
        response = requests.post(
            self.restful_endpoint + "position", headers=headers, data=data)
        lg.info("Got response: {} with header: {}".format(
            response.status_code, response.headers))
        result = json.loads(response.content.decode())
        lg.info("Result: {}".format(result))
        assert "result" in result
        assert "OK" == result["result"]

    def test_websocket_commands(self):
        lg.info("Testing websocket commands")
        with connect(self.websocket_endpoint) as conn:
            # we don't need a stream parser and buffer for websocket connections because
            # websocket is much higher in level compared to serial interfaces... and the
            # library actually already manages packaging and buffering for us.
            lg.info("Opened websocket connection.")
            lg.info("Authenticating")
            auth_msg = {"token": self.auth["access_token"]}
            auth_msg = json.dumps(auth_msg)
            conn.send(auth_msg)
            result = conn.recv()
            lg.info("Authentication result: {}".format(result))
            
            lg.info("Setting position via websocket...")
            action_msg = {"position": {"value": 123456}}
            action_msg = json.dumps(action_msg)
            conn.send(action_msg)
            result = conn.recv()
            lg.info("Action result: {}".format(result))
            result = conn.recv()
            lg.info("Additional message: {}".format(result))
            
            lg.info("Setting position via websocket, with command id...")
            action_msg = {"position": {"value": 654321}, "id": 114514}
            action_msg = json.dumps(action_msg)
            conn.send(action_msg)
            result = conn.recv()
            lg.info("Action result: {}".format(result))
            result = conn.recv()
            lg.info("Additional message: {}".format(result))
