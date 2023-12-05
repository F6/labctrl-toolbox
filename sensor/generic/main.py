# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231126"

# std libs
import logging
import asyncio
from enum import Enum
from typing import Annotated, Optional
from json import JSONDecodeError
from contextlib import asynccontextmanager
# third party libs
from fastapi import Depends, FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError, Field
# this package
from .sensor import SensorActionResult
from .sensor import sensor_controller as sc
from .server_config import server_config, UserAccessLevel
from .hardware_config import hardware_config, SensorConfig
from .hardware_config import dump_config_to_file as dump_hardware_config
from .auth import try_authenticate, create_access_token, validate_access_token
from .auth import Token, TokenData, AccessLevelException, check_access_level
from .ws import WebSocketConnectionManager, WSContinuousSamplingResultSender
from .unit import TemperatureQuantity, HumidityQuantity, SensorTemperatureUnit, SensorHumidityUnit, TimeQuantity


lg = logging.getLogger(__name__)


class ServerStatusReport(BaseModel):
    status: str


class ServerResourceNames(BaseModel):
    resources: list[str]


class SensorOperationResult(BaseModel):
    result: SensorActionResult


class LogicalQuantity(BaseModel):
    value: int


class SensorDataReport(BaseModel):
    temperature: Optional[LogicalQuantity] = Field(
        None, description="Temperature logical value.")
    humidity: Optional[LogicalQuantity] = Field(
        None, description="Humidity logical value.")
    absolute_temperature: Optional[TemperatureQuantity] = Field(
        None, description="Temperature value with unit."
    )
    absolute_humidity: Optional[HumidityQuantity] = Field(
        None, description="Humidity value with unit."
    )


class SensorParameterReport(BaseModel):
    parameter: SensorConfig


class SensorParameterSetOperation(BaseModel):
    temperature_sampling_interval: Optional[TimeQuantity] = Field(
        None, description="Temperature Sampling Interval, must specify both a value and a unit.")
    humidity_sampling_interval: Optional[TimeQuantity] = Field(
        None, description="Humidity Sampling Interval, must specify both a value and a unit."
    )
    continuous_sampling_mode: Optional[bool] = Field(
        None, description="Turn on continuous sampling mode if given true, turn off continuous sampling mode if given false, do nothing if None.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start SensorController and corresponding threads
    sc.start()
    yield
    # Clean up resources, gracefully shut down SensorController
    sc.stop()
    # save hardware config on exit so that next time the user does not need to set up again.
    lg.warning("Saving current hardware config at server side.")
    dump_hardware_config(hardware_config)

ws_mgr = WebSocketConnectionManager()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.CORS.origins,
    allow_credentials=server_config.CORS.allow_credentials,
    allow_methods=server_config.CORS.allow_methods,
    allow_headers=server_config.CORS.allow_headers,
)


@app.get("/")
async def get_resource_names() -> ServerResourceNames:
    r = ['status',
         'token',
         'data',
         'parameter',
         'ws(ws://)']
    return ServerResourceNames(resources=r)


@app.get("/status")
async def get_server_status() -> ServerStatusReport:
    return ServerStatusReport(status="OK")


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    authenticate_result, user = try_authenticate(
        server_config.auth.users, form_data.username, form_data.password)
    if authenticate_result is False:
        # don't tell the user if it is the username or the password that is wrong.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # authentication successful, create token
    access_token = create_access_token(user=user)
    return Token(**{"access_token": access_token, "token_type": "bearer"})


@app.get("/data")
async def get_sensor_data(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SensorDataReport:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    temperature = LogicalQuantity(value=sc.get_temperature())
    humidity = LogicalQuantity(value=sc.get_humidity())
    return SensorDataReport(
        temperature=temperature,
        humidity=humidity,
        absolute_temperature=sc.get_absolute_temperature(),
        absolute_humidity=sc.get_absolute_humidity())


@app.get("/data/temperature")
async def get_temperature(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> LogicalQuantity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    value = sc.get_temperature()
    return LogicalQuantity(value=value)


@app.get("/data/absolute_temperature")
async def get_absolute_temperature(
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> TemperatureQuantity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_absolute_temperature()


@app.get("/data/humidity")
async def get_humidity(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> LogicalQuantity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    value = sc.get_humidity()
    return LogicalQuantity(value=value)


@app.get("/data/absolute_humidity")
async def get_absolute_humidity(
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> HumidityQuantity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_absolute_humidity()


@app.get("/parameter")
async def get_parameter(
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SensorParameterReport:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return SensorParameterReport(parameter=hardware_config.sensor)


@app.post("/parameter")
async def set_parameter(
        parameter_update: SensorParameterSetOperation,
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SensorOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    result = SensorActionResult.OK
    if parameter_update.temperature_sampling_interval is not None:
        action_result = sc.set_absolute_temperature_sampling_interval(
            interval=parameter_update.temperature_sampling_interval.value,
            unit=parameter_update.temperature_sampling_interval.unit
        )
        if action_result is SensorActionResult.OK:
            pass
        else:
            result = SensorActionResult.ERROR_GENERIC
    if parameter_update.humidity_sampling_interval is not None:
        action_result = sc.set_absolute_humidity_sampling_interval(
            interval=parameter_update.humidity_sampling_interval.value,
            unit=parameter_update.humidity_sampling_interval.unit
        )
        if action_result is SensorActionResult.OK:
            pass
        else:
            result = SensorActionResult.ERROR_GENERIC
    if parameter_update.continuous_sampling_mode is not None:
        if parameter_update.continuous_sampling_mode:
            # when we turn on the continuous sampling mode, start to broadcast measurement results to all clients.
            message_handler = WSContinuousSamplingResultSender(ws_mgr)
            action_result = sc.start_continuous_sampling_mode(
                message_handler=message_handler)
        else:
            action_result = sc.stop_continuous_sampling_mode()
    return SensorOperationResult(result=result)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    wsid = None
    try:
        wsid = await ws_mgr.connect(websocket)
        await ws_mgr.run(wsid)
    except WebSocketDisconnect as e:
        # user disconnected from client side.
        lg.debug(
            "User disconnected from WebSocket connection, normal disconnection: {}".format(e))
    except JSONDecodeError:
        # user sent non-json message, probably wrong client, disconnect right away.
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    except ValidationError:
        # user input lack required field or malformed, report error to user and disconnect right away.
        await websocket.send_json({"error": "Invalid Operation"})
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    except AccessLevelException:
        # user input is legal and the user is good, but the user does not have the permission to perform the operation.
        await websocket.send_json({"error": "Insufficient Access Level"})
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    finally:
        if wsid is None:
            lg.info(
                "Client disconnected from websocket before authentication and protocol initialization finish.")
        else:
            # clear websocket and application protocol stored in manager as well as its auth info.
            ws_mgr.disconnect(wsid)
