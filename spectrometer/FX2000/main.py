# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"

# std libs
import logging
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
from .spectrometer import SpectrometerActionResult
from .spectrometer import spectrometer_controller as sc
from .server_config import server_config, UserAccessLevel
from .hardware_config import hardware_config, SpectrometerConfig
from .hardware_config import dump_config_to_file as dump_hardware_config
from .auth import try_authenticate, create_access_token, validate_access_token
from .auth import Token, TokenData, AccessLevelException, check_access_level
from .ws import WebSocketConnectionManager
from .unit import TimeQuantity


lg = logging.getLogger(__name__)


class ServerStatusReport(BaseModel):
    status: str


class ServerResourceNames(BaseModel):
    resources: list[str]


class SpectrometerOperationResult(BaseModel):
    result: SpectrometerActionResult


class SpectrometerWavelengthsReport(BaseModel):
    wavelengths: list[float]


class SpectrometerSpectrumReport(BaseModel):
    spectrum: list[int]


class SpectrometerParameterReport(BaseModel):
    parameter: SpectrometerConfig


class SpectrometerParameterSetOperation(BaseModel):
    integration_time: Optional[TimeQuantity] = Field(
        None, description="Integration time, must specify both a value and a unit.")
    boxcar_width: Optional[int] = Field(
        None, description="Boxcar width."
    )
    average_times: Optional[int] = Field(
        None, description="Average Times.")


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
         'wavelengths',
         'spectrum',
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


@app.get("/wavelengths")
async def get_spectrometer_wavelengths(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SpectrometerWavelengthsReport:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    wavelengths = sc.get_wavelengths()
    return SpectrometerWavelengthsReport(
        wavelengths=wavelengths)


@app.get("/spectrum")
async def get_spectrometer_spectrum(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SpectrometerSpectrumReport:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    spectrum = sc.get_spectrum()
    return SpectrometerSpectrumReport(spectrum=spectrum)


@app.get("/parameter")
async def get_parameter(
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SpectrometerParameterReport:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return SpectrometerParameterReport(parameter=hardware_config.spectrometer)


@app.post("/parameter")
async def set_parameter(
        parameter_update: SpectrometerParameterSetOperation,
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> SpectrometerOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    result = SpectrometerActionResult.OK
    if parameter_update.integration_time is not None:
        action_result = sc.set_integration_time_with_unit(
            value=parameter_update.integration_time.value,
            unit=parameter_update.integration_time.unit
        )
        if action_result is SpectrometerActionResult.OK:
            pass
        else:
            result = SpectrometerActionResult.ERROR_GENERIC
    if parameter_update.boxcar_width is not None:
        action_result = sc.set_boxcar_width(
            value=parameter_update.boxcar_width
        )
        if action_result is SpectrometerActionResult.OK:
            pass
        else:
            result = SpectrometerActionResult.ERROR_GENERIC
    if parameter_update.average_times is not None:
        action_result = sc.set_average_times(
            value=parameter_update.average_times
        )
        if action_result is SpectrometerActionResult.OK:
            pass
        else:
            result = SpectrometerActionResult.ERROR_GENERIC

    return SpectrometerOperationResult(result=result)


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
