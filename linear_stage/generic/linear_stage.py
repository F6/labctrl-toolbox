# -*- coding: utf-8 -*-

"""linear_stage.py:
This module provides the LinearStageController class to control a linear stage connected via a serial port, 
such as the CDHD2 linear motor driver & controller.

Concepts:

*Absolute position and logical position*: 

Absolute position is the distance between the stage and the home switch of the linear stage. 
It is a real world physical quantity, thus is represented (roughly) by a float number and a unit.
This representation is inaccurate and may eventually introduce errors that accumulate during relative operations and unit conversions.
Most motor controllers and position sensors works with discrete quantities.
For example, stepper motors can only rotate to certain angles called steps.
If the stepper motor has 100 steps per revolution, and is connected to a leadscrew with pitch 1mm, 
then your linear stage can only hold at discrete positions such as 10um, 20um, 30um, etc.. 
It cannot hold its position at other places accurately, such as 13um, 17um.
For linear motors/BLDC/PMSM, although the driving resolution is quite high, 
the minimum discrete step length is usually limited by the encoder (i.e. the position sensor) resolution.
Because these motors works in a closed loop, for each specific motor,
we can only determine its current position by looking at the position sensor,
whose output must be quantized at some stage of the feedback system.
Thus they also work in the discrete domain.
Thus, internally, we use logical position to represent the current position of the linear stage accurately.
The logical position is the number of tiny steps that is required to move the stage from origin to current position:

    (logical position) * (physical length of a step) = (absolute position) * (unit)

For example, for the above leadscrew linear stage, the physical length of a step is 10um,
becase we cannot reliably reach precision level beyond 10um. 
So if it is currently at around 1145.14 mm away from the origin, then its logical position is the integer 114514.
The logical position is an integer, there's no error or rounding is introduced during calculation, 
thus it is safe to use for precise/relative operations.
The linear stage cannot operate reliably beyond the precision represented by 1 logical position difference, 
thus the logical position is also the most precise representation of the actual physical distance available.
For example, for the above leadscrew linear stage, if its current logical position is 114514,
then the actual physical position might be 1145.141919810mm, or 1145.140000000mm, 
or other values that can be rounded to 1145.14mm. 
However, because the stage can only operate up to the precision level of 0.01mm, 
1145.141919810mm or 1145.140000000mm does not make a difference for operating the stage.

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import logging
from enum import Enum
from typing import Optional
# third party
from pydantic import BaseModel, Field
# this project
from serial_helper import SerialManager
from .hardware_config import HardwareConfig, hardware_config
from .unit import stage_unit_converter
from .unit import StageDisplacementUnit, StageVelocityUnit, StageAccelerationUnit
from .unit import StageDisplacement, StageVelocity, StageAcceleration
# set up logging
lg = logging.getLogger(__name__)


class StageOperation(BaseModel):
    position: Optional[int] = Field(
        None, description="Logical value of target position.")
    absolute_position: Optional[StageDisplacement] = Field(
        None, description="Absolute position, with a unit.")
    velocity: Optional[StageVelocity] = Field(
        None, description="Sets stage velocity, with a unit.")
    acceleration: Optional[StageAcceleration] = Field(
        None, description="Sets stage acceleration, with a unit.")


class LinearStageActionResult(Enum):
    OK = "OK"
    ERROR_GENERIC = "error_generic"  # one or multiple errors happend
    WARN_NO_ACTION = "warn_no_action"  # no action is performed
    SOFT_LIMIT_EXCEEDED = "soft_limit_exceeded"
    SERIAL_RW_FAILURE = "serial_RW_failure"
    INVALID_ACTION = "invalid_action"
    RESPONSE_VALIDATION_FAILURE = "response_validation_failure"


class LinearStageController:
    def __init__(
            self, ser_mgr: SerialManager, config: HardwareConfig) -> None:
        self.ser_mgr = ser_mgr
        self.config = config
        # this shallow copy points to dict in config, so that when dumping config, current position is saved
        self.position = config.parameter.position.default_value
        self.command_id: int = 0
        lg.debug("LinearStageController initialzed.")

    def start(self):
        lg.info("Starting LinearStageController")
        self.ser_mgr.start()
        lg.info("LinearStageController started.")

    def stop(self):
        lg.info("Gracefully shutting down LinearStageController")
        self.ser_mgr.stop()
        lg.info("LinearStageController stopped.")

    def command(self, s: str):
        lg.debug("Sending command {}".format(s))
        self.command_id += 1
        self.ser_mgr.send(s.encode('ascii'), message_id=self.command_id)
        # wait for sending confirmation
        t_send, sid_returned = self.ser_mgr.sent_id_queue.get()
        # wait for response
        t_receive, response = self.ser_mgr.receive()
        # check for matching
        # [TODO]
        return response.decode()

    def __warn_no_action(self, value):
        lg.warning(
            "Target value is the same as current value {}!".format(
                value)
        )
        lg.warning(
            "This usually happens when operating beyond the precision of the stage, or system is out of sync. Check docs for more explanation."
        )
        lg.warning(
            "Sending command anyway."
        )

    def move_to_position(self, position: int) -> LinearStageActionResult:
        result = LinearStageActionResult.OK
        position_config = self.config.parameter.position
        if (position > position_config.maximum) \
                or (position < position_config.minimum):
            lg.error(
                "Target position exceeds soft limit, target={}, limit=({}, {}).".format(
                    position,
                    position_config.minimum,
                    position_config.maximum
                ))
            return LinearStageActionResult.SOFT_LIMIT_EXCEEDED
        if position == self.position:
            self.__warn_no_action(position)
            result = LinearStageActionResult.WARN_NO_ACTION
        lg.debug("Moving stage to position {}".format(position))
        # because the stage accepts command in milimeter and second units, convert units before sending command.
        # convert logical position to absolute position
        abs_pos_value = position * position_config.unit_step.value
        abs_pos_in_mm = stage_unit_converter.convert(
            abs_pos_value, position_config.unit_step.unit, StageDisplacementUnit.MILIMETER)
        speed_in_mm_s = stage_unit_converter.convert(
            self.config.parameter.velocity.value, self.config.parameter.velocity.unit_step.unit, StageVelocityUnit.MILIMETER_PER_SECOND)
        r = self.command('MOVEABS {pos:.4f} {speed:.4f}\r'.format(
            pos=abs_pos_in_mm, speed=speed_in_mm_s))
        self.position = position
        lg.debug("Response from device: {}".format(r))
        # [TODO]: validate if r is the same as defined in protocol
        return result

    def move_to_absolute_position(self, abs_pos: float, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> LinearStageActionResult:
        target_pos_value = stage_unit_converter.convert(
            abs_pos, unit, self.config.parameter.position.unit_step.unit)
        target_pos_value = int(
            target_pos_value / self.config.parameter.position.unit_step.value)
        return self.move_to_position(target_pos_value)

    def get_absolute_position(self, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> StageDisplacement:
        abs_pos_value = self.position * self.config.parameter.position.unit_step.value
        abs_pos_value = stage_unit_converter.convert(
            abs_pos_value, self.config.parameter.position.unit_step.unit, unit)
        return StageDisplacement(value=abs_pos_value, unit=unit)

    def set_velocity(self, velocity: float, unit: StageVelocityUnit = StageVelocityUnit.MILIMETER_PER_SECOND) -> LinearStageActionResult:
        target_value = stage_unit_converter.convert(
            velocity, unit, self.config.parameter.velocity.unit_step.unit)
        target_value = int(
            target_value / self.config.parameter.velocity.unit_step.value)
        self.config.parameter.velocity.value = target_value
        return LinearStageActionResult.OK

    def set_acceleration(self, acceleration: float, unit: StageAccelerationUnit = StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED) -> LinearStageActionResult:
        target_value = stage_unit_converter.convert(
            acceleration, unit, self.config.parameter.acceleration.unit_step.unit)
        target_value = int(
            target_value / self.config.parameter.acceleration.unit_step.value)
        self.config.parameter.acceleration.value = target_value
        return LinearStageActionResult.OK

    def stage_operation(self, operation: StageOperation) -> LinearStageActionResult:
        # sanity check: Don't provide both position and absolute_position.
        if operation.position is not None and operation.absolute_position is not None:
            return LinearStageActionResult.INVALID_ACTION
        # start of operaiton
        if operation.acceleration is not None:
            result = self.set_acceleration(
                operation.acceleration.value, operation.acceleration.unit)
            if result is not LinearStageActionResult.OK:
                return result
        if operation.velocity is not None:
            result = self.set_velocity(
                operation.velocity.value, operation.velocity.unit)
            if result is not LinearStageActionResult.OK:
                return result
        if operation.absolute_position is not None:
            result = self.move_to_absolute_position(
                operation.absolute_position.value, operation.absolute_position.unit)
            if result is not LinearStageActionResult.OK:
                return result
        if operation.position is not None:
            result = self.move_to_position(operation.position)
            if result is not LinearStageActionResult.OK:
                return result
        # end of operation, if everthing is OK, return OK.
        return LinearStageActionResult.OK


# create LinearStageController that all threads shares according to config.
serial_config = hardware_config.serial
ser_mgr = SerialManager(
    serial_config.port, baudrate=serial_config.baudrate, timeout=serial_config.timeout)

# ----- FOR TESTING
IS_TESTING = True
if IS_TESTING:
    from .hardware_mocker import mocked_ser
    ser_mgr.ser = mocked_ser
# ===== END FOR TESTING

linear_stage_controller = LinearStageController(ser_mgr, hardware_config)
