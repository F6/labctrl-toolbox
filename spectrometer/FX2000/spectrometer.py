# -*- coding: utf-8 -*-

"""spectrometer.py:
This module provides the SpectrometerController class to control a spectrometer.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"

# std libs
import logging
from enum import Enum
# third party
import numpy as np
# this project
from .hardware_config import HardwareConfig, hardware_config
from .FX import FX2000
from .unit import spectrometer_unit_converter, SpectrometerTimeUnit
# set up logging
lg = logging.getLogger(__name__)


class SpectrometerActionResult(Enum):
    OK = "OK"
    ERROR_GENERIC = "error_generic"  # one or multiple errors happend
    WARN_NO_ACTION = "warn_no_action"  # no action is performed
    SOFT_LIMIT_EXCEEDED = "soft_limit_exceeded"
    DISCONNECTED = "disconnected"
    INVALID_ACTION = "invalid_action"
    RESPONSE_VALIDATION_FAILURE = "response_validation_failure"
    DEVICE_ERROR = "device_error"


class SpectrometerController:
    def __init__(
            self, spectrometer: FX2000, config: HardwareConfig) -> None:
        self.sm = spectrometer
        self.config = config
        lg.debug("SpectrometerController initialzed.")

    def start(self):
        lg.info("Starting SpectrometerController")
        lg.info("SpectrometerController started.")

    def stop(self):
        lg.info("Gracefully shutting down SpectrometerController")
        lg.info("SpectrometerController stopped.")

    def get_name(self) -> str:
        return self.sm.name

    def get_wavelengths(self):
        return self.sm.wavelengths
        # wavelengths = self.sm.wavelengths
        # return np.array(wavelengths, dtype=np.float64)

    def get_spectrum(self):
        return self.sm.get_spectrum()
        # spectrum = self.sm.get_spectrum()
        # return np.array(spectrum, dtype=np.float64)

    def __warn_no_action(self, value):
        lg.warning("Target value is the same as current value: {}".format(value))
        lg.warning(
            "This usually happens when operating beyond the available precision, or system is out of sync. Check docs for more explanation."
        )
        lg.warning("Sending command anyway.")

    def __check_soft_limit_exceeded(self, value: int, minimum: int, maximum: int) -> bool:
        if (value > maximum) or (value < minimum):
            lg.error(
                "Target value exceeds soft limit, target={}, limit=({}, {}).".format(
                    value,
                    minimum,
                    maximum
                ))
            return True
        else:
            return False

    def set_integration_time(self, value: int) -> SpectrometerActionResult:
        result = SpectrometerActionResult.OK
        # Check for soft limit
        param_config = self.config.spectrometer.integration_time
        if self.__check_soft_limit_exceeded(value, param_config.minimum, param_config.maximum):
            return SpectrometerActionResult.SOFT_LIMIT_EXCEEDED
        # check for precision limit
        if value == param_config.value:
            self.__warn_no_action(value)
            result = SpectrometerActionResult.WARN_NO_ACTION
        # perform the operation
        lg.debug("Setting integration time: {}".format(value))
        value_ms = spectrometer_unit_converter.convert(
            value * param_config.unit_step.value,
            param_config.unit_step.unit,
            SpectrometerTimeUnit.MILISECOND
        )
        self.sm.set_integration_time(value_ms)
        param_config.value = value
        return result

    def set_integration_time_with_unit(self, value: float, unit: SpectrometerTimeUnit) -> SpectrometerActionResult:
        cfg = self.config.spectrometer.integration_time
        target_value = spectrometer_unit_converter.convert(
            value,
            unit,
            cfg.unit_step.unit
        )
        target_value = int(target_value / cfg.unit_step.value)
        return self.set_integration_time(target_value)

    def set_boxcar_width(self, value: int) -> SpectrometerActionResult:
        result = SpectrometerActionResult.OK
        # Check for soft limit
        param_config = self.config.spectrometer.boxcar_width
        if self.__check_soft_limit_exceeded(value, param_config.minimum, param_config.maximum):
            return SpectrometerActionResult.SOFT_LIMIT_EXCEEDED
        # check for precision limit
        if value == param_config.value:
            self.__warn_no_action(value)
            result = SpectrometerActionResult.WARN_NO_ACTION
        # perform the operation
        lg.debug("Setting boxcar width: {}".format(value))
        self.sm.set_boxcar_width(value)
        param_config.value = value
        return result

    def set_average_times(self, value: int) -> SpectrometerActionResult:
        result = SpectrometerActionResult.OK
        # Check for soft limit
        param_config = self.config.spectrometer.average_times
        if self.__check_soft_limit_exceeded(value, param_config.minimum, param_config.maximum):
            return SpectrometerActionResult.SOFT_LIMIT_EXCEEDED
        # check for precision limit
        if value == param_config.value:
            self.__warn_no_action(value)
            result = SpectrometerActionResult.WARN_NO_ACTION
        # perform the operation
        lg.debug("Setting average times: {}".format(value))
        self.sm.set_average_times(value)
        param_config.value = value
        return result

# create SpectrometerController that all threads shares according to config.


# ----- FOR TESTING
IS_TESTING = True
if IS_TESTING:
    from .hardware_mocker import MockedFX2000
    spectrometer = MockedFX2000()
else:
    spectrometer = FX2000()
# ===== END FOR TESTING

spectrometer_controller = SpectrometerController(spectrometer, hardware_config)
