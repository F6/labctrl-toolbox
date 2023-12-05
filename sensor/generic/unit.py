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


class SensorTemperatureUnit(GenericUnit):
    KELVIN = "K"
    DEGREE_CELSIUS = "degC"
    DEGREE_FAHRENHEIT = "degF"


class SensorHumidityUnit(GenericUnit):
    GRAM_PER_CUBIC_METER = "g/(m^3)"
    RELATIVE_HUMIDITY = "RH"
    PERCENT_RELATIVE_HUMIDITY = "%RH"


class SensorTimeUnit(GenericUnit):
    SECOND = "s"
    MILISECOND = "ms"
    MICROSECOND = "us"
    NANOSECOND = "ns"


class UnitConverter():
    def __init__(self) -> None:
        self.rules: dict[tuple[GenericUnit, GenericUnit], Callable[[float], float]] = {
            (SensorTemperatureUnit.KELVIN, SensorTemperatureUnit.KELVIN): lambda k: k,
            (SensorTemperatureUnit.KELVIN, SensorTemperatureUnit.DEGREE_CELSIUS): lambda k: k - 273.15,
            (SensorTemperatureUnit.KELVIN, SensorTemperatureUnit.DEGREE_FAHRENHEIT): lambda k: (k - 273.15) * 9/5 + 32,
            (SensorTemperatureUnit.DEGREE_CELSIUS, SensorTemperatureUnit.KELVIN): lambda x: x + 273.15,
            (SensorTemperatureUnit.DEGREE_CELSIUS, SensorTemperatureUnit.DEGREE_CELSIUS): lambda x: x,
            (SensorTemperatureUnit.DEGREE_CELSIUS, SensorTemperatureUnit.DEGREE_FAHRENHEIT): lambda x: (x * 9/5) + 32,
            (SensorTemperatureUnit.DEGREE_FAHRENHEIT, SensorTemperatureUnit.KELVIN): lambda x: (x - 32) * 5/9 + 273.15,
            (SensorTemperatureUnit.DEGREE_FAHRENHEIT, SensorTemperatureUnit.DEGREE_CELSIUS): lambda x: (x - 32) * 5/9,
            (SensorTemperatureUnit.DEGREE_FAHRENHEIT, SensorTemperatureUnit.DEGREE_FAHRENHEIT): lambda x: x,
            (SensorTimeUnit.SECOND, SensorTimeUnit.SECOND): lambda x: x * 1e0,
            (SensorTimeUnit.SECOND, SensorTimeUnit.MILISECOND): lambda x: x * 1e3,
            (SensorTimeUnit.SECOND, SensorTimeUnit.MICROSECOND): lambda x: x * 1e6,
            (SensorTimeUnit.SECOND, SensorTimeUnit.NANOSECOND): lambda x: x * 1e9,
            (SensorTimeUnit.MILISECOND, SensorTimeUnit.SECOND): lambda x: x * 1e-3,
            (SensorTimeUnit.MILISECOND, SensorTimeUnit.MILISECOND): lambda x: x * 1e0,
            (SensorTimeUnit.MILISECOND, SensorTimeUnit.MICROSECOND): lambda x: x * 1e3,
            (SensorTimeUnit.MILISECOND, SensorTimeUnit.NANOSECOND): lambda x: x * 1e6,
            (SensorTimeUnit.MICROSECOND, SensorTimeUnit.SECOND): lambda x: x * 1e-6,
            (SensorTimeUnit.MICROSECOND, SensorTimeUnit.MILISECOND): lambda x: x * 1e-3,
            (SensorTimeUnit.MICROSECOND, SensorTimeUnit.MICROSECOND): lambda x: x * 1e0,
            (SensorTimeUnit.MICROSECOND, SensorTimeUnit.NANOSECOND): lambda x: x * 1e3,
            (SensorTimeUnit.NANOSECOND, SensorTimeUnit.SECOND): lambda x: x * 1e-9,
            (SensorTimeUnit.NANOSECOND, SensorTimeUnit.MILISECOND): lambda x: x * 1e-6,
            (SensorTimeUnit.NANOSECOND, SensorTimeUnit.MICROSECOND): lambda x: x * 1e-3,
            (SensorTimeUnit.NANOSECOND, SensorTimeUnit.NANOSECOND): lambda x: x * 1e0,
            (SensorHumidityUnit.PERCENT_RELATIVE_HUMIDITY, SensorHumidityUnit.PERCENT_RELATIVE_HUMIDITY): lambda x: x,
            (SensorHumidityUnit.RELATIVE_HUMIDITY, SensorHumidityUnit.RELATIVE_HUMIDITY): lambda x: x,
            (SensorHumidityUnit.GRAM_PER_CUBIC_METER, SensorHumidityUnit.GRAM_PER_CUBIC_METER): lambda x: x,
        }
        # [TODO]: implement humidity conversion.
        # humidity conversion are special because they require additional environment parameters
        self.convert_humidity = self.convert

    def convert(self, quantity: float, unit_from: GenericUnit, unit_to: GenericUnit):
        return self.rules[(unit_from, unit_to)](quantity)


sensor_unit_converter = UnitConverter()


class TemperatureQuantity(BaseModel):
    value: float
    unit: SensorTemperatureUnit


class HumidityQuantity(BaseModel):
    value: float
    unit: SensorHumidityUnit


class TimeQuantity(BaseModel):
    value: float
    unit: SensorTimeUnit
