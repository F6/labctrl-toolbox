# -*- coding: utf-8 -*-

"""unit.py:
This module provides unit definitions and conversion table for current device.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"

# std libs
from enum import Enum
from typing import Callable
# third-party
from pydantic import BaseModel
# We can probably use pint to deal with units in the future.
# However, for now the pint package is not well-adapted to pydantic models and new typing features
# of python. And the unit JSON serialization/deserialization is also quite complicated.
# Thus, we will wait for some years to see if it works in the future.
# For now, we will simply use Enums for unit conversion.
# This is awkward, but effective for simple unit conversions.

# from pint import UnitRegistry
# ureg = UnitRegistry()


# To get a starting point to edit the unit conversion rules, you can use script like this
# q = "SensorTemperatureUnit"
# s = ['KELVIN', 'DEGREE_CELSIUS', 'DEGREE_FAHRENHEIT']
# for (ii, i) in enumerate(s):
#     for (jj, j) in enumerate(s):
#         print(f"({q}.{i}, {q}.{j}): lambda x:x,")

# For kilo-mili type unit conversion, you can directly use this to get the conversion rules
# q = "SensorTimeUnit"
# s = ['SECOND', 'MILISECOND', 'MICROSECOND', 'NANOSECOND']
# for (ii, i) in enumerate(s):
#     for (jj, j) in enumerate(s):
#         t = - (ii - jj) * 3
#         print(f"({q}.{i}, {q}.{j}): lambda x:x * 1e{t},")


class GenericUnit(str, Enum):
    pass


class SpectrometerTemperatureUnit(GenericUnit):
    KELVIN = "K"
    DEGREE_CELSIUS = "degC"
    DEGREE_FAHRENHEIT = "degF"

class SpectrometerTimeUnit(GenericUnit):
    SECOND = "s"
    MILISECOND = "ms"
    MICROSECOND = "us"
    NANOSECOND = "ns"


class UnitConverter():
    def __init__(self) -> None:
        self.rules: dict[tuple[GenericUnit, GenericUnit], Callable[[float], float]] = {
            (SpectrometerTemperatureUnit.KELVIN, SpectrometerTemperatureUnit.KELVIN): lambda k: k,
            (SpectrometerTemperatureUnit.KELVIN, SpectrometerTemperatureUnit.DEGREE_CELSIUS): lambda k: k - 273.15,
            (SpectrometerTemperatureUnit.KELVIN, SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT): lambda k: (k - 273.15) * 9/5 + 32,
            (SpectrometerTemperatureUnit.DEGREE_CELSIUS, SpectrometerTemperatureUnit.KELVIN): lambda x: x + 273.15,
            (SpectrometerTemperatureUnit.DEGREE_CELSIUS, SpectrometerTemperatureUnit.DEGREE_CELSIUS): lambda x: x,
            (SpectrometerTemperatureUnit.DEGREE_CELSIUS, SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT): lambda x: (x * 9/5) + 32,
            (SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT, SpectrometerTemperatureUnit.KELVIN): lambda x: (x - 32) * 5/9 + 273.15,
            (SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT, SpectrometerTemperatureUnit.DEGREE_CELSIUS): lambda x: (x - 32) * 5/9,
            (SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT, SpectrometerTemperatureUnit.DEGREE_FAHRENHEIT): lambda x: x,
            (SpectrometerTimeUnit.SECOND, SpectrometerTimeUnit.SECOND): lambda x: x * 1e0,
            (SpectrometerTimeUnit.SECOND, SpectrometerTimeUnit.MILISECOND): lambda x: x * 1e3,
            (SpectrometerTimeUnit.SECOND, SpectrometerTimeUnit.MICROSECOND): lambda x: x * 1e6,
            (SpectrometerTimeUnit.SECOND, SpectrometerTimeUnit.NANOSECOND): lambda x: x * 1e9,
            (SpectrometerTimeUnit.MILISECOND, SpectrometerTimeUnit.SECOND): lambda x: x * 1e-3,
            (SpectrometerTimeUnit.MILISECOND, SpectrometerTimeUnit.MILISECOND): lambda x: x * 1e0,
            (SpectrometerTimeUnit.MILISECOND, SpectrometerTimeUnit.MICROSECOND): lambda x: x * 1e3,
            (SpectrometerTimeUnit.MILISECOND, SpectrometerTimeUnit.NANOSECOND): lambda x: x * 1e6,
            (SpectrometerTimeUnit.MICROSECOND, SpectrometerTimeUnit.SECOND): lambda x: x * 1e-6,
            (SpectrometerTimeUnit.MICROSECOND, SpectrometerTimeUnit.MILISECOND): lambda x: x * 1e-3,
            (SpectrometerTimeUnit.MICROSECOND, SpectrometerTimeUnit.MICROSECOND): lambda x: x * 1e0,
            (SpectrometerTimeUnit.MICROSECOND, SpectrometerTimeUnit.NANOSECOND): lambda x: x * 1e3,
            (SpectrometerTimeUnit.NANOSECOND, SpectrometerTimeUnit.SECOND): lambda x: x * 1e-9,
            (SpectrometerTimeUnit.NANOSECOND, SpectrometerTimeUnit.MILISECOND): lambda x: x * 1e-6,
            (SpectrometerTimeUnit.NANOSECOND, SpectrometerTimeUnit.MICROSECOND): lambda x: x * 1e-3,
            (SpectrometerTimeUnit.NANOSECOND, SpectrometerTimeUnit.NANOSECOND): lambda x: x * 1e0,
        }

    def convert(self, quantity: float, unit_from: GenericUnit, unit_to: GenericUnit):
        return self.rules[(unit_from, unit_to)](quantity)


spectrometer_unit_converter = UnitConverter()


class TemperatureQuantity(BaseModel):
    value: float
    unit: SpectrometerTemperatureUnit

class TimeQuantity(BaseModel):
    value: float
    unit: SpectrometerTimeUnit
