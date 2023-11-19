# -*- coding: utf-8 -*-

"""api.py:
Python API for shutter toolbox server.
The library allows you to simply call methods to control remote shutters, as if they are local python objects.
This library is a wrapping over the web interface provided by the toolbox server, not the hardware-level API provided in
the toolbox server.
To access hardware directly, check readme.md for the toolbox for the hardware API documentation.

You can include this API by importing this package directly with

    >>> import toolbox.shutter.api.python as remote_shutter

or you can simply copy this file with config.json to your project directory, because this file is actually independent
from the toolbox server and can be used alone.

The controller class uses threading to monitor remote status constantly, keep WebSocket connection open,
and manage authentication expiration events.
So you need to call close method on the object to quit gracefully.
If the connections are not closed gracefully, the program may halt on exit.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import logging
import json
import threading
import time
import datetime
# third-party libs
import requests
import jwt
from websockets.sync.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosed
# this package
from .config import load_config_from_file, dump_config_to_file

lg = logging.getLogger(__name__)


class RemoteShutter():
    def __init__(self, config_path: str | None = None) -> None:
        lg.info("Reading config file.")
        if config_path is None:
            self.config = load_config_from_file()
        else:
            self.config = load_config_from_file(config_path=config_path)
        # load connection info
        cfg = self.config.restful
        self.restful_endpoint = "{protocol}{host}:{port}{endpoint}".format(
            protocol=cfg.protocol, host=cfg.host, port=cfg.port, endpoint=cfg.endpoint)
        cfg = self.config.websocket
        self.websocket_endpoint = "{protocol}{host}:{port}{endpoint}".format(
            protocol=cfg.protocol, host=cfg.host, port=cfg.port, endpoint=cfg.endpoint)
        self.auth_header = self.config.authentication.token_type + \
            " " + self.config.authentication.access_token
        # initialize state flags and watchdogs
        #   restful
        lg.info("Checking RESTful service available...")
        self.restful_available = self.check_restful_availability()
        lg.info("Retriving shutter list from remote...")
        self.shutter_list = self.get_shutter_list()
        lg.info("Retrived shutter list: {}".format(self.shutter_list))
        #   authentication
        lg.info("Checking authentication status")
        self.pending_reauthentication = self.check_reauthentication_required()
        lg.info("Reauthentication needed: {}".format(
            self.pending_reauthentication))
        if self.pending_reauthentication:
            lg.info("Authenticating client...")
            self.handle_reauthenticate()
        self.authentication_watchdog_running = False
        self.authentication_watchdog_thread = threading.Thread(
            target=self.__authentication_watchdog_task)
        #   shutter states
        self.shutter_states: dict[str, str] = dict()
        lg.info("Updating local shutter states from remote...")
        for shutter_name in self.shutter_list:
            r = self.get_shutter_state(shutter_name=shutter_name)
            self.shutter_states[shutter_name] = r["state"]
        lg.info("Current states: {}".format(self.shutter_states))
        self.shutter_state_watchdog_running = False
        self.shutter_state_watchdog_thread = threading.Thread(
            target=self.__shutter_state_watchdog_task)
        self.initiate_watchdogs()
        # initialize websocket connection handlers
        self.websocket_handler_running = False
        self.websocket_connection_pool: dict[str, ClientConnection] = dict()
        self.websocket_handler_threadpool: dict[str, threading.Thread] = dict()
        lg.info("Creating websocket handlers...")
        for shutter_name in self.shutter_list:
            websocket_handler_thread = threading.Thread(
                target=self.__websocket_handler_task,
                kwargs={"shutter_name": shutter_name}
            )
            self.websocket_handler_threadpool[shutter_name] = websocket_handler_thread
        self.initiate_websockets()
        # construct a dict that represents websocket command execution states
        self.websocket_command_status: dict[int, str | None] = dict()
        self.websocket_command_id = 0

    def initiate_watchdogs(self) -> None:
        lg.info("Starting authentication watchdog thread...")
        self.authentication_watchdog_running = True
        self.authentication_watchdog_thread.start()
        lg.info("Starting shutter state watchdog thread...")
        self.shutter_state_watchdog_running = True
        self.shutter_state_watchdog_thread.start()

    def close_watchdogs(self) -> None:
        lg.info("Gracefully halting authentication watchdog...")
        self.authentication_watchdog_running = False
        self.authentication_watchdog_thread.join()
        lg.info("Gracefully halting shutter state watchdog...")
        self.shutter_state_watchdog_running = False
        self.shutter_state_watchdog_thread.join()

    def initiate_websockets(self) -> None:
        """
        Connects to the WebSocket server and authenticates the connections for each shutter
        Auto reconnects if closed
        """
        self.websocket_handler_running = True
        for shutter_name in self.shutter_list:
            lg.info(
                "Starting websocket handler for shutter {}...".format(shutter_name))
            self.websocket_handler_threadpool[shutter_name].start()

    def close_websockets(self) -> None:
        lg.info("Gracefully disconnecting all websockets...")
        self.websocket_handler_running = False
        for shutter_name in self.shutter_list:
            lg.info(
                "Waiting for all messages from shutter {} are handled before closing websocket connection...".format(shutter_name))
            self.websocket_connection_pool[shutter_name].close()
            self.websocket_handler_threadpool[shutter_name].join()

    def __authentication_watchdog_task(self):
        """
        Checks authentication status constantly and reauthenticates this client when needed.
        """
        while self.authentication_watchdog_running:
            # check authentication locally
            # (does not request remote to validate token because validation is quite time-consuming)
            self.pending_reauthentication = self.check_reauthentication_required()
            if self.pending_reauthentication:
                self.handle_reauthenticate()
            time.sleep(1.0)

    def check_reauthentication_required(self) -> bool:
        """
        Checks for JWT expiration and empty JWT locally.
        Note that this only verifies the basic token formats and time, it does not verify the signature.
        Use validate_token if a full remote validation is needed.
        """
        # check for empty access token
        if self.config.authentication.access_token == "":
            lg.info("Empty JWT, reauthentication is required.")
            return True
        # check for token basic format and expiration
        try:
            decoded = jwt.decode(
                self.config.authentication.access_token,
                options={"verify_signature": False})  # works in PyJWT >= v2.0
            tnow = datetime.datetime.now(tz=datetime.UTC)
            texp = datetime.datetime.fromtimestamp(
                decoded["exp"], tz=datetime.UTC)
            if (texp - tnow) < datetime.timedelta(seconds=30):
                lg.info("Reauthencitation is required before token expiration!")
                lg.info("Time now is {}".format(
                    tnow.strftime("%Y-%m-%d %H:%M:%S")))
                lg.info("Time to expire is {}".format(
                    texp.strftime("%Y-%m-%d %H:%M:%S")))
                # 30 seconds until expiration
                return True
        except jwt.exceptions.DecodeError as e:
            # malformed JWT, reauthenticate to correct it.
            lg.info("Reauthentication required because local JWT cannot be decoded: {}".format(e))
            return True
        except KeyError as e:
            # no expiration time found in decoded token, it must be invalid.
            lg.info("Cannot fint {} field in JWT! Is this JWT correct?".format(e))
            return True
        return False

    def handle_reauthenticate(self) -> None:
        """
        Tries to authenticate this client, callback for the .authenticate method.
        This callback catches exceptions, so a outer loop is required for automatic retry.
        """
        try:
            self.authenticate()
        except AssertionError:
            lg.error(
                "Authentication failed, check the credentials provided in config.")
        except requests.exceptions.RequestException as e:
            lg.error(
                "Cannot access authentication service, check the connection status: {}".format(e))
        except Exception as e:
            lg.error(
                "Unexpected error occured during re-authentication. Error is {}".format(e))

    def authenticate(self) -> None:
        """
        Tries to authenticate this client using credentials provided in config.
        """
        lg.info("Authenticating client.")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": self.config.authentication.username,
            "password": self.config.authentication.password
        }
        response = requests.post(self.restful_endpoint + "token",
                                 headers=headers,
                                 data=data)
        result = json.loads(response.content.decode())
        assert "access_token" in result
        lg.info("Successfully logged in, token type: {}".format(
            result["token_type"]))
        self.config.authentication.access_token = result["access_token"]
        self.config.authentication.token_type = result["token_type"]
        self.auth_header = result["token_type"] + " " + result["access_token"]
        dump_config_to_file(self.config)

    def __shutter_state_watchdog_task(self):
        """
        Checks for remote availability and shutter states constantly.
        """
        while self.shutter_state_watchdog_running:
            # poll for shutter state every second, to keep up with server if other clients changed server states
            for shutter_name in self.shutter_list:
                r = self.get_shutter_state(shutter_name=shutter_name)
                self.shutter_states[shutter_name] = r["state"]
            time.sleep(1.0)

    def __websocket_handler_task(self, shutter_name: str):
        endpoint = self.websocket_endpoint + shutter_name
        while self.websocket_handler_running:
            try:
                with connect(endpoint) as ws:
                    lg.info("Opened a new websocket connection. Authenticating")
                    auth_msg = {
                        "token": self.config.authentication.access_token}
                    auth_msg = json.dumps(auth_msg)
                    ws.send(auth_msg)
                    result = ws.recv()
                    lg.info("Authentication result: {}".format(result))
                    self.websocket_connection_pool[shutter_name] = ws
                    lg.info("Listening to new websocket to handle messages...")
                    while True:
                        message = ws.recv()
                        self.handle_websocket_message(message)
            except ConnectionClosed:
                lg.warning(
                    "Websocket disconnected, if not halting, reconnection will be scheduled.")
                continue
        lg.info("Websocket handler task done.")

    def handle_websocket_message(self, message: str):
        try:
            r = json.loads(message)
            if "id" in r:
                self.websocket_command_status[r["id"]] = r["result"]
            if "shutter_name" in r:
                self.shutter_states[r["shutter_name"]] = r["state"]
        except ValueError as e:
            lg.warning("Non-JSON data received, error is {}".format(e))
        except KeyError as e:
            lg.warning("Cannot parse message: {}: {}".format(message, e))

    def close(self):
        lg.info("Halting connection to remote shutter.")
        self.close_watchdogs()
        self.close_websockets()
        lg.info("Closed all connection to remote shutter cleanly.")

    def check_restful_availability(self) -> bool:
        """
        Checks for RESTful API availability by requesting the /status RESTful endpoint.
        """
        available = False
        try:
            response = requests.get(self.restful_endpoint + "status")
            result = json.loads(response.content.decode())
            if result["status"] == "OK":
                available = True
        except requests.exceptions.RequestException as e:
            lg.warning("Connection lost, reason: {}".format(e))
        except ValueError as e:
            lg.warning("Non-JSON data received, error is {}".format(e))
        except KeyError as e:
            lg.warning("Server responded non-status message, {}".format(e))
        except Exception as e:
            lg.error(
                "Unexpected error when checking RESTful API availability, error is {}".format(e))
        finally:
            return available

    def check_websocket_availability(self, shutter_name: str) -> bool:
        """
        Checks for WebSocket availability by sending a PING frame.
        If the remote WebSocket server is active, it should respond with a PONG frame ASAP.
        """
        available = False
        try:
            pong_event = self.websocket_connection_pool[shutter_name].ping()
            # wait for pong for 2.0 second, the threading.Event.wait returns True if event set.
            available = pong_event.wait(timeout=2.0)
        except ConnectionClosed:
            lg.warning("WebSocket connection closed unexpectedly.")
        except KeyError as e:
            lg.warning("WebSocket for shutter {} is not ready yet!".format(shutter_name))
        except Exception as e:
            lg.error(
                "Unexpected error occured during websocket availability checking, error is {errtype} - {err}, {args}".format(errtype=type(e).__name__, err=e, args=e.args))
        finally:
            return available

    def get_shutter_list(self):
        response = requests.get(self.restful_endpoint)
        result = json.loads(response.content.decode())
        return result["shutter_list"]

    def get_shutter_state(self, shutter_name: str):
        headers = {
            "accept": "application/json",
            "Authorization": self.auth_header
        }
        response = requests.get(
            self.restful_endpoint + shutter_name, headers=headers)
        result = json.loads(response.content.decode())
        return result

    def restful_command(self, resource_path: str, command: str):
        headers = {
            "accept": "application/json",
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "action": command
        }).encode()
        response = requests.post(
            self.restful_endpoint + resource_path, headers=headers, data=data)
        result = json.loads(response.content.decode())
        return result

    def rest_turn_on(self, shutter_name: str):
        return self.restful_command(resource_path=shutter_name, command="ON")

    def rest_turn_off(self, shutter_name: str):
        return self.restful_command(resource_path=shutter_name, command="OFF")

    def rest_switch(self, shutter_name: str):
        return self.restful_command(resource_path=shutter_name, command="SWITCH")

    def websocket_command(self, shutter_name: str, command: str, cid: int | None = None, timeout: float | None = None) -> int:
        """
        Send a command to the given shutter. Returns the ID of the command.
        Optional:
            - You can attach an ID to the command with the `cid` parameter, the ID can be used to check 
            command status later in another place by looking up value in .websocket_command_status, the ID 
            does not need to be unique, but keep in mind that non-unique ID commands shares the same 
            status.
            - You can specify a timeout to block the function execution until a response from server is 
            received. If the execution time exceeds the timeout, TimeoutError is raised. By default 
            timeout is None, and the function does not block. Set timeout to 0 to wait the server forever 
            and never timeout.
        Notes:
            If a cid is not provided, the method uses an internal cid that is unique to each call.
        """
        t0 = time.time()
        if cid is None:
            # generate unique internal cid and use it
            self.websocket_command_id += 1
            cid = self.websocket_command_id
        # before sending command, set status to None. This status is shared with __websocket_handler_task and is modified in that thread when response is received.
        self.websocket_command_status[cid] = None
        data = json.dumps({"action": command, "id": cid})
        self.websocket_connection_pool[shutter_name].send(data)
        if timeout is None:
            # No timeout specified, return immediately.
            return cid
        else:
            # timeout used
            while True:
                tnow = time.time()
                if (timeout != 0) and ((tnow - t0) > timeout):
                    raise TimeoutError
                if self.websocket_command_status[cid]:
                    return cid
                time.sleep(0.01)

    def turn_on(self, shutter_name: str, timeout: float | None = None):
        return self.websocket_command(shutter_name=shutter_name,
                               command="ON", timeout=timeout)

    def turn_off(self, shutter_name: str, timeout: float | None = None):
        return self.websocket_command(shutter_name=shutter_name,
                               command="OFF", timeout=timeout)

    def switch(self, shutter_name: str, timeout: float | None = None):
        return self.websocket_command(shutter_name=shutter_name,
                               command="SWITCH", timeout=timeout)
