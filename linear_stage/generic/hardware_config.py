# -*- coding: utf-8 -*-

"""hardware_config.py:
This module defines the data model of config file for the hardware of this application.
It also provides methods to load config from config file, or dump config to a file.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import os
import json
from typing import Optional
# third party libs
from pydantic import BaseModel
# this package
from .unit import StageDisplacementUnit, StageVelocityUnit, StageAccelerationUnit
# meta params and defaults
HARDWARE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'hardware.config.json')


class SerialConfig(BaseModel):
    port: str
    timeout: float
    baudrate: int


class StagePosition(BaseModel):
    value: int


class StageDisplacement(BaseModel):
    value: float
    unit: StageDisplacementUnit


class StageVelocity(BaseModel):
    value: float
    unit: StageVelocityUnit


class StageAcceleration(BaseModel):
    value: float
    unit: StageAccelerationUnit


class StageOperation(BaseModel):
    position: Optional[StagePosition] = None
    absolute_position: Optional[StageDisplacement] = None
    velocity: Optional[StageVelocity] = None
    acceleration: Optional[StageAcceleration] = None


class StageSoftLimit(BaseModel):
    minimum: int  # use logical position
    maximum: int  # use logical position


class StageConfig(BaseModel):
    velocity: StageVelocity
    acceleration: StageAcceleration
    unit_step: StageDisplacement
    soft_limit: StageSoftLimit
    default_position: StagePosition  # use logical position


class HardwareConfig(BaseModel):
    serial: SerialConfig
    stage: StageConfig


def load_config_from_file(config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'r') as f:
        r = json.load(f)
    return HardwareConfig(**r)


def dump_config_to_file(config: HardwareConfig, config_path: str = HARDWARE_CONFIG_PATH):
    with open(config_path, 'w+') as f:
        f.write(config.model_dump_json(indent=4))


hardware_config = load_config_from_file()
