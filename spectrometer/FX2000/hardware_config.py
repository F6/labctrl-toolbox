# -*- coding: utf-8 -*-

"""hardware_config.py:
This module defines the data model of config file for the hardware of this application.
It also provides methods to load config from config file, or dump config to a file.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"

# std libs
import os
import json
from typing import Optional
# third party libs
from pydantic import BaseModel
# this package
from .unit import TimeQuantity, TemperatureQuantity
# meta params and defaults
HARDWARE_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 'hardware.config.json')


class IntegrationTimeConfig(BaseModel):
    unit_step: TimeQuantity
    value: int
    minimum: int
    maximum: int


class BoxcarWidthConfig(BaseModel):
    value: int
    minimum: int
    maximum: int


class AverageTimesConfig(BaseModel):
    value: int
    minimum: int
    maximum: int


class SpectrometerConfig(BaseModel):
    integration_time: IntegrationTimeConfig
    boxcar_width: BoxcarWidthConfig
    average_times: AverageTimesConfig


class HardwareConfig(BaseModel):
    spectrometer: SpectrometerConfig


def load_config_from_file(config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'r') as f:
        r = json.load(f)
    return HardwareConfig(**r)


def dump_config_to_file(config: HardwareConfig, config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'w+') as f:
        f.write(config.model_dump_json(indent=4))


hardware_config = load_config_from_file()
