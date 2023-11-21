# std libs
from enum import Enum
# third-party

# We can probably use pint to deal with units in the future.
# However, for now the pint package is not well-adapted to pydantic models and new typing features
# of python. And the unit JSON serialization/deserialization is also quite complicated.
# Thus, we will wait for some years to see if it works in the future.
# For now, we will simply use Enums for unit conversion.
# This is awkward, but effective for simple unit conversions.

# from pint import UnitRegistry
# ureg = UnitRegistry()


# Generate unit conversion table for kilo-mili-type units
# q = "StageDisplacementUnit"
# s = ['NANOMETER', 'MICROMETER', 'MILIMETER', 'METER']
# for (ii, i) in enumerate(s):
#     for (jj, j) in enumerate(s):
#         t = (ii - jj)*3
#         print(f"({q}.{i}, {q}.{j}): 1e{t},")


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
        self.mapping = {
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.NANOMETER): 1e0,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.MICROMETER): 1e-3,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.MILIMETER): 1e-6,
            (StageDisplacementUnit.NANOMETER, StageDisplacementUnit.METER): 1e-9,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.NANOMETER): 1e3,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.MICROMETER): 1e0,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.MILIMETER): 1e-3,
            (StageDisplacementUnit.MICROMETER, StageDisplacementUnit.METER): 1e-6,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.NANOMETER): 1e6,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.MICROMETER): 1e3,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.MILIMETER): 1e0,
            (StageDisplacementUnit.MILIMETER, StageDisplacementUnit.METER): 1e-3,
            (StageDisplacementUnit.METER, StageDisplacementUnit.NANOMETER): 1e9,
            (StageDisplacementUnit.METER, StageDisplacementUnit.MICROMETER): 1e6,
            (StageDisplacementUnit.METER, StageDisplacementUnit.MILIMETER): 1e3,
            (StageDisplacementUnit.METER, StageDisplacementUnit.METER): 1e0,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): 1e0,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): 1e-3,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): 1e-6,
            (StageVelocityUnit.NANOMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): 1e-9,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): 1e3,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): 1e0,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): 1e-3,
            (StageVelocityUnit.MICROMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): 1e-6,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): 1e6,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): 1e3,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): 1e0,
            (StageVelocityUnit.MILIMETER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): 1e-3,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.NANOMETER_PER_SECOND): 1e9,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.MICROMETER_PER_SECOND): 1e6,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.MILIMETER_PER_SECOND): 1e3,
            (StageVelocityUnit.METER_PER_SECOND, StageVelocityUnit.METER_PER_SECOND): 1e0,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): 1e0,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): 1e-3,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): 1e-6,
            (StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): 1e-9,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): 1e3,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): 1e0,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): 1e-3,
            (StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): 1e-6,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): 1e6,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): 1e3,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): 1e0,
            (StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): 1e-3,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.NANOMETER_PER_SECOND_SQUARED): 1e9,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.MICROMETER_PER_SECOND_SQUARED): 1e6,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED): 1e3,
            (StageAccelerationUnit.METER_PER_SECOND_SQUARED, StageAccelerationUnit.METER_PER_SECOND_SQUARED): 1e0,
        }

    def convert(self, quantity: float, unit_from: GenericUnit, unit_to: GenericUnit):
        return quantity * self.mapping[(unit_from, unit_to)]

stage_unit_converter = UnitConverter()