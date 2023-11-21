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
# third party

# this project
from serial_helper import SerialManager
from .hardware_config import HardwareConfig, StageDisplacement, StageOperation
from .unit import stage_unit_converter, StageDisplacementUnit, StageVelocityUnit, StageAccelerationUnit
# set up logging
lg = logging.getLogger(__name__)


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
        self.position = config.stage.default_position
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
        self.ser_mgr.send(s.encode('ascii'), sent_id=self.command_id)
        # wait for sending confirmation
        t_send, sid_returned = self.ser_mgr.sent_id_queue.get()
        # wait for response
        t_receive, response = self.ser_mgr.receive()
        # check for matching
        # [TODO]
        return response.decode()

    def move_to_position(self, position: int) -> LinearStageActionResult:
        result = LinearStageActionResult.OK
        if (position > self.config.stage.soft_limit.maximum) \
                or (position < self.config.stage.soft_limit.minimum):
            lg.error(
                "Target position exceeds soft limit, target={}, limit=({}, {}).".format(
                    position,
                    self.config.stage.soft_limit.minimum,
                    self.config.stage.soft_limit.maximum
                ))
            return LinearStageActionResult.SOFT_LIMIT_EXCEEDED
        if position == self.position.value:
            lg.warning(
                "Target position is the same as current position {}!".format(
                    position)
            )
            lg.warning(
                "This usually happens when operating beyond the precision of the stage, or system is out of sync. Check docs for more explanation."
            )
            lg.warning(
                "Sending command anyway."
            )
            result = LinearStageActionResult.WARN_NO_ACTION
        lg.debug("Moving stage to position {}".format(position))
        # because the stage accepts command in milimeter and second units, convert units before sending command.
        # convert logical position to absolute position
        abs_pos_value = position * self.config.stage.unit_step.value
        abs_pos_in_mm = stage_unit_converter.convert(
            abs_pos_value, self.config.stage.unit_step.unit, StageDisplacementUnit.MILIMETER)
        speed_in_mm_s = stage_unit_converter.convert(
            self.config.stage.velocity.value, self.config.stage.velocity.unit, StageVelocityUnit.MILIMETER_PER_SECOND)
        r = self.command('MOVEABS {pos:.4f} {speed:.4f}\r'.format(
            pos=abs_pos_in_mm, speed=speed_in_mm_s))
        self.position.value = position
        lg.debug("Response from device: {}".format(r))
        # [TODO]: validate if r is the same as defined in protocol
        return result

    def move_to_absolute_position(self, abs_pos: float, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> LinearStageActionResult:
        target_pos_value = stage_unit_converter.convert(
            abs_pos, unit, self.config.stage.unit_step.unit
        )
        target_pos_value = int(
            target_pos_value / self.config.stage.unit_step.value)
        return self.move_to_position(target_pos_value)

    def get_absolute_position(self, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> StageDisplacement:
        abs_pos_value = self.position.value * self.config.stage.unit_step.value
        abs_pos_value = stage_unit_converter.convert(
            abs_pos_value, self.config.stage.unit_step.unit, unit)
        return StageDisplacement(value=abs_pos_value, unit=unit)

    def set_velocity(self, velocity: float, unit: StageVelocityUnit = StageVelocityUnit.MILIMETER_PER_SECOND) -> LinearStageActionResult:
        self.config.stage.velocity.value = velocity
        self.config.stage.velocity.unit = unit
        return LinearStageActionResult.OK

    def set_acceleration(self, acceleration: float, unit: StageAccelerationUnit = StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED) -> LinearStageActionResult:
        self.config.stage.acceleration.value = acceleration
        self.config.stage.acceleration.unit = unit
        return LinearStageActionResult.OK

    def stage_operation(self, operation: StageOperation) -> LinearStageActionResult:
        if (operation.position != None) and (operation.absolute_position != None):
            return LinearStageActionResult.INVALID_ACTION
        r_acc, r_vel, r_pos = LinearStageActionResult.OK, LinearStageActionResult.OK, LinearStageActionResult.OK
        if operation.acceleration:
            r_acc = self.set_acceleration(
                operation.acceleration.value, operation.acceleration.unit)
        if operation.velocity:
            r_vel = self.set_velocity(operation.velocity.value,
                                      operation.velocity.unit)
        if operation.position:
            r_pos = self.move_to_position(position=operation.position.value)
        elif operation.absolute_position:
            r_pos = self.move_to_absolute_position(
                abs_pos=operation.absolute_position.value, unit=operation.absolute_position.unit)
        else:
            pass
        if (r_acc is LinearStageActionResult.OK) and (r_pos is LinearStageActionResult.OK) and (r_vel is LinearStageActionResult.OK):
            return LinearStageActionResult.OK
        else:
            return LinearStageActionResult.ERROR_GENERIC
