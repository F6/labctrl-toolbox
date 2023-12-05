# -*- coding: utf-8 -*-

"""hardware_config.py:
This module defines the data model of config file for the hardware of this application.
It also provides methods to load config from config file, or dump config to a file.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231123"

# std libs
import os
import json
from typing import Optional
# third party libs
from pydantic import BaseModel
# this package
from .unit import TimeQuantity, TemperatureQuantity, HumidityQuantity
# meta params and defaults
HARDWARE_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 'hardware.config.json')


class SerialConfig(BaseModel):
    port: str
    timeout: float
    baudrate: int


class SamplingIntervalConfig(BaseModel):
    unit_step: TimeQuantity
    value: int
    minimum: int
    maximum: int


class ParameterConfig(BaseModel):
    pass


class TemperatureSensorConfig(ParameterConfig):
    unit_step: TemperatureQuantity
    sampling_interval: SamplingIntervalConfig


class HumiditySensorConfig(ParameterConfig):
    unit_step: HumidityQuantity
    sampling_interval: SamplingIntervalConfig


class SensorConfig(BaseModel):
    temperature: TemperatureSensorConfig
    humidity: HumiditySensorConfig


class HardwareConfig(BaseModel):
    serial: SerialConfig
    sensor: SensorConfig


def load_config_from_file(config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'r') as f:
        r = json.load(f)
    return HardwareConfig(**r)


def dump_config_to_file(config: HardwareConfig, config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'w+') as f:
        f.write(config.model_dump_json(indent=4))


hardware_config = load_config_from_file()
