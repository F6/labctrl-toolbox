
# -*- coding: utf-8 -*-

"""unit.py:
This module provides unit definitions and unit conversion rules for the device.

We can probably use pint to deal with units in the future.
However, for now the pint package is not well-adapted to pydantic models and new typing features
of python. And the unit JSON serialization/deserialization is also quite complicated.
Thus, we will wait for some years to see if it works in the future.
For now, we will simply use Enums for unit conversion.
This is awkward, but effective for simple unit conversions.

    from pint import UnitRegistry
    ureg = UnitRegistry()
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

# std libs
from enum import Enum
from typing import Callable
# third-party
from pydantic import BaseModel

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


class GenericUnit(Enum):
    pass


class StageDisplacementUnit(GenericUnit):
    NANOMETER = "nm"
    MICROMETER = "um"
    MILIMETER = "mm"
    METER = "m"


class StageVelocityUnit(GenericUnit):
    NANOMETER_PER_SECOND = "nm/s"
    MICROMETER_PER_SECOND = "um/s"
    MILIMETER_PER_SECOND = "mm/s"
    METER_PER_SECOND = "m/s"


class StageAccelerationUnit(GenericUnit):
    NANOMETER_PER_SECOND_SQUARED = "nm/(s^2)"
    MICROMETER_PER_SECOND_SQUARED = "um/(s^2)"
    MILIMETER_PER_SECOND_SQUARED = "mm/(s^2)"
    METER_PER_SECOND_SQUARED = "m/(s^2)"


class UnitConverter():
    def __init__(self) -> None:
        self.rules: dict[tuple[GenericUnit, GenericUnit], Callable[[float], float]] = {
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.NANOMETER): lambda x: x * 1e0,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.MICROMETER): lambda x: x * 1e-3,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.MILIMETER): lambda x: x * 1e-6,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.METER): lambda x: x * 1e-9,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.NANOMETER): lambda x: x * 1e3,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.MICROMETER): lambda x: x * 1e0,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.MILIMETER): lambda x: x * 1e-3,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.METER): lambda x: x * 1e-6,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.NANOMETER): lambda x: x * 1e6,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.MICROMETER): lambda x: x * 1e3,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.MILIMETER): lambda x: x * 1e0,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.METER): lambda x: x * 1e-3,
            (StageDisplacementUnit.METER, StageDisplacementUnit.NANOMETER): lambda x: x * 1e9,
            (StageDisplacementUnit.METER, StageDisplacementUnit.MICROMETER): lambda x: x * 1e6,
            (StageDisplacementUnit.METER, StageDisplacementUnit.MILIMETER): lambda x: x * 1e3,
            (StageDisplacementUnit.METER, StageDisplacementUnit.METER): lambda x: x * 1e0,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): lambda x: x * 1e0,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): lambda x: x * 1e-3,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): lambda x: x * 1e-6,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): lambda x: x * 1e-9,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): lambda x: x * 1e3,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): lambda x: x * 1e0,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): lambda x: x * 1e-3,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): lambda x: x * 1e-6,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): lambda x: x * 1e6,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): lambda x: x * 1e3,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): lambda x: x * 1e0,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): lambda x: x * 1e-3,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): lambda x: x * 1e9,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): lambda x: x * 1e6,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): lambda x: x * 1e3,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): lambda x: x * 1e0,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): lambda x: x * 1e0,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): lambda x: x * 1e-3,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): lambda x: x * 1e-6,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): lambda x: x * 1e-9,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): lambda x: x * 1e3,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): lambda x: x * 1e0,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): lambda x: x * 1e-3,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): lambda x: x * 1e-6,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): lambda x: x * 1e6,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): lambda x: x * 1e3,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): lambda x: x * 1e0,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): lambda x: x * 1e-3,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): lambda x: x * 1e9,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): lambda x: x * 1e6,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): lambda x: x * 1e3,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): lambda x: x * 1e0,
        }

    def convert(self, quantity: float, unit_from: GenericUnit, unit_to: GenericUnit):
        return self.rules[(unit_from, unit_to)](quantity)


stage_unit_converter = UnitConverter()


class StageDisplacement(BaseModel):
    value: float
    unit: StageDisplacementUnit


class StageVelocity(BaseModel):
    value: float
    unit: StageVelocityUnit


class StageAcceleration(BaseModel):
    value: float
    unit: StageAccelerationUnit
