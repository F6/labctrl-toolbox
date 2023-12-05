# -*- coding: utf-8 -*-

"""
labctrl/toolbox/sensor/generic:

## Introduction

This package provides remote API for a sensor controller with authentication.
Several interfaces are provided:

1. RESTful API over HTTP protocol for non-blocking asynchronous operations.

2. WebSocket RPC interface for time-critical operations.

See readme.md in parent directory for usage documentation.

## Package

    - sensor.py: provides SensorController class as an asynchronous interface to manage and operate the sensor.
    - unit.py: provides basic unit definitions and conversion tools for physical quantities.
    - main.py: FastAPI application for HTTP API and WebSocket endpoint.
    - auth.py: authentication module for generating and varifying JWTs.
    - hardware_config.py: data model for hardware config.
    - server_config.py: data model for server config.
    - hardware_mocker: mocks a true device for testing.
    - ws.py: websocket message parsing and responsing module.

## Scripts
    - register.py: generates a new user config according to input and insert it into config file.

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"


import logging
lg = logging.getLogger(__name__)

from .sensor import SensorController, SensorActionResult
lg.info("toolbox.sensor.generic imported.")