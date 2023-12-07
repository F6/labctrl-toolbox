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

*Physical Quantity and Logical Quantity*:

Similar to absolute position and logical position, controlling a device also requires 
other physical quantities to be represented, such as velocity and acceleration.
These quantities also can only be measured and constrained to some certain level of
precision, and if we use the smallest achievable step as the unit step, it is also possible
to represent the physical quantity precisely as an integer, and we call this representation
a logical quantity.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

# std libs
import logging
from enum import Enum
from typing import Optional
from abc import ABC, abstractmethod
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


class DeviceStateUpdateHandler(ABC):
    """
    Abstract class, User can implement this class to handle device state update events.
    The handle_update method is hooked into every device method that changes local state.
    This is useful when multiple clients are accessing the same device.
    When one client asked for a state change, for example updating a parameter, other
    clients can be notified in the handle_update hook.
    """
    @abstractmethod
    def handle_update(self, update: dict):
        pass


class StageOperation(BaseModel):
    position: Optional[int | StageDisplacement] = Field(
        None, description="Target position, logical value if int, physical value if with a unit.")
    velocity: Optional[int | StageVelocity] = Field(
        None, description="Sets stage velocity, logical value if int, physical value if with a unit.")
    acceleration: Optional[int | StageAcceleration] = Field(
        None, description="Sets stage acceleration, logical value if int, physical value if with a unit.")


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
            self, ser_mgr: SerialManager, config: HardwareConfig, update_hook: DeviceStateUpdateHandler | None = None) -> None:
        self.ser_mgr = ser_mgr
        self.config = config
        # the update hook can be attached at initialization, or any time later if other components are not ready yet.
        self.update_hook = update_hook
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

    def __compare_identical_and_warn_no_action(self, value_before, value_after) -> bool:
        """
        This method is called just before attempting to change a state value.
        It compares the two values, and if they are the same, fire some warnings in the logging and returns True,
        because in normal circumstances, people will not call for a change if no change is needed.
        If the are not the same, returns False.
        """
        if value_before == value_after:
            lg.warning(
                "Target value is the same as current value {}!".format(
                    value_before)
            )
            lg.warning(
                "This usually happens when operating beyond the precision of the device, or system is out of sync. Check docs for more explanation."
            )
            lg.warning(
                "Sending command anyway."
            )
            return True
        else:
            return False

    def __check_value_within_limits(self, value, minimum, maximum) -> bool:
        """
        This method is called just before attempting to change a state value.
        It compares the value to be changed with it's limitation.
        If the value is within the limits, returns True.
        If the value is out of limits, fire some errors in the logging and returns False.
        """
        if (value > maximum) or (value < minimum):
            lg.error(
                "Target value exceeds soft limit, target={}, limit=({}, {}).".format(
                    value,
                    minimum,
                    maximum
                ))
            return False
        else:
            return True

    def get_position(self) -> int:
        return self.position

    def set_position(self, position: int) -> LinearStageActionResult:
        result = LinearStageActionResult.OK
        cfg = self.config.parameter.position
        if not self.__check_value_within_limits(position, cfg.minimum, cfg.maximum):
            return LinearStageActionResult.SOFT_LIMIT_EXCEEDED
        if self.__compare_identical_and_warn_no_action(self.position, position):
            result = LinearStageActionResult.WARN_NO_ACTION
        # ======== Start of command execution ========
        lg.debug("Moving stage to position {}".format(position))
        # because the stage accepts command in milimeter and second units, convert units before sending command.
        # convert logical position to absolute position
        abs_pos_value = position * cfg.unit_step.value
        abs_pos_in_mm = stage_unit_converter.convert(
            abs_pos_value, cfg.unit_step.unit, StageDisplacementUnit.MILIMETER)
        speed_in_mm_s = stage_unit_converter.convert(
            self.config.parameter.velocity.value, self.config.parameter.velocity.unit_step.unit, StageVelocityUnit.MILIMETER_PER_SECOND)
        r = self.command('MOVEABS {pos:.4f} {speed:.4f}\r'.format(
            pos=abs_pos_in_mm, speed=speed_in_mm_s))
        # [TODO]: validate if r is the same as defined in protocol
        lg.debug("Response from device: {}".format(r))
        # ======== End of command execution ========
        self.position = position
        if self.update_hook is not None:
            self.update_hook.handle_update({"position": position})
        return result

    def get_absolute_position(self, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> StageDisplacement:
        cfg = self.config.parameter.position
        position = self.position * cfg.unit_step.value
        position_in_target_unit = stage_unit_converter.convert(
            position, cfg.unit_step.unit, unit)
        return StageDisplacement(value=position_in_target_unit, unit=unit)

    def set_absolute_position(self, abs_pos: float, unit: StageDisplacementUnit = StageDisplacementUnit.MILIMETER) -> LinearStageActionResult:
        cfg = self.config.parameter.position
        target_pos_value = stage_unit_converter.convert(
            abs_pos, unit, cfg.unit_step.unit)
        target_pos_value = int(target_pos_value / cfg.unit_step.value)
        return self.set_position(target_pos_value)

    def get_velocity(self) -> int:
        return self.config.parameter.velocity.value

    def set_velocity(self, target_value: int) -> LinearStageActionResult:
        result = LinearStageActionResult.OK
        cfg = self.config.parameter.velocity
        if not self.__check_value_within_limits(target_value, cfg.minimum, cfg.maximum):
            return LinearStageActionResult.SOFT_LIMIT_EXCEEDED
        if self.__compare_identical_and_warn_no_action(cfg.value, target_value):
            result = LinearStageActionResult.WARN_NO_ACTION
        self.config.parameter.velocity.value = target_value
        # ======== Start of setting velocity ========
        # because CDHD2 we use sends velocity along with position commands, no need for additional commands.
        # ======== End of setting velocity ========
        if self.update_hook is not None:
            self.update_hook.handle_update({"velocity": target_value})
        return result

    def get_physical_velocity(self, unit: StageVelocityUnit = StageVelocityUnit.MILIMETER_PER_SECOND) -> StageVelocity:
        cfg = self.config.parameter.velocity
        velocity = cfg.value * cfg.unit_step.value
        velocity_in_target_unit = stage_unit_converter.convert(
            velocity, cfg.unit_step.unit, unit)
        return StageDisplacement(value=velocity_in_target_unit, unit=unit)

    def set_physical_velocity(self, velocity: float, unit: StageVelocityUnit = StageVelocityUnit.MILIMETER_PER_SECOND) -> LinearStageActionResult:
        cfg = self.config.parameter.velocity
        target_value = stage_unit_converter.convert(
            velocity, unit, cfg.unit_step.unit)
        target_value = int(target_value / cfg.unit_step.value)
        return self.set_velocity(target_value)

    def get_acceleration(self) -> int:
        return self.config.parameter.acceleration.value

    def set_acceleration(self, target_value: int) -> LinearStageActionResult:
        result = LinearStageActionResult.OK
        cfg = self.config.parameter.acceleration
        if not self.__check_value_within_limits(target_value, cfg.minimum, cfg.maximum):
            return LinearStageActionResult.SOFT_LIMIT_EXCEEDED
        if self.__compare_identical_and_warn_no_action(cfg.value, target_value):
            result = LinearStageActionResult.WARN_NO_ACTION
        self.config.parameter.acceleration.value = target_value
        # ======== Start of setting acceleration ========
        # because CDHD2 we use sends acceleration along with position commands, no need for additional commands.
        # ======== End of setting acceleration ========
        if self.update_hook is not None:
            self.update_hook.handle_update({"acceleration": target_value})
        return result

    def get_physical_acceleration(self, unit: StageAccelerationUnit = StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED) -> StageAcceleration:
        cfg = self.config.parameter.acceleration
        acceleration = cfg.value * cfg.unit_step.value
        acceleration_in_target_unit = stage_unit_converter.convert(
            acceleration, cfg.unit_step.unit, unit)
        return StageAcceleration(value=acceleration_in_target_unit, unit=unit)

    def set_physical_acceleration(self, acceleration: float, unit: StageAccelerationUnit = StageAccelerationUnit.MILIMETER_PER_SECOND_SQUARED) -> LinearStageActionResult:
        cfg = self.config.parameter.acceleration
        target_value = stage_unit_converter.convert(
            acceleration, unit, cfg.unit_step.unit)
        target_value = int(target_value / cfg.unit_step.value)
        return self.set_acceleration(target_value)

    def stage_operation(self, operation: StageOperation) -> LinearStageActionResult:
        # start of operation. We can only do isinstance like this because python does not has
        # multiple dispatch support... very ugly but should be clean.
        all_ok = True
        if isinstance(operation.acceleration, int):
            result = self.set_acceleration(operation.acceleration)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        if isinstance(operation.acceleration, StageAcceleration):
            result = self.set_physical_acceleration(
                operation.acceleration.value, operation.acceleration.unit)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        if isinstance(operation.velocity, int):
            result = self.set_velocity(operation.velocity)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        if isinstance(operation.velocity, StageVelocity):
            result = self.set_physical_velocity(
                operation.velocity.value, operation.velocity.unit)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        if isinstance(operation.position, int):
            result = self.set_position(operation.position)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        if isinstance(operation.position, StageDisplacement):
            result = self.set_absolute_position(
                operation.position.value, operation.position.unit)
            if result is not LinearStageActionResult.OK:
                all_ok = False
        # end of operation, if everthing is OK, return OK.
        if all_ok:
            return LinearStageActionResult.OK
        else:
            return LinearStageActionResult.ERROR_GENERIC

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
