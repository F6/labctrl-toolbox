# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

# std libs
import logging
from typing import Annotated
from json import JSONDecodeError
from contextlib import asynccontextmanager
# third party libs
from websockets.exceptions import ConnectionClosedOK
from fastapi import Depends, FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
# this package
from .linear_stage import LinearStageActionResult, StageOperation
from .linear_stage import linear_stage_controller as sc
from .server_config import server_config, UserAccessLevel
from .hardware_config import hardware_config, StageDisplacement, StageVelocity, StageAcceleration
from .hardware_config import StageParameter, StagePositionParameter, StageAccelerationParameter, StageVelocityParameter
from .hardware_config import dump_config_to_file as dump_hardware_config
from .auth import try_authenticate, create_access_token, validate_access_token, check_access_level
from .auth import Token, TokenData, AccessLevelException
from .ws import WebSocketConnectionManager, WSDeviceStateUpdateSender

lg = logging.getLogger(__name__)


class LogicalQuantitiy(BaseModel):
    value: int


class ServerStatusReport(BaseModel):
    status: str


class ServerResourceNames(BaseModel):
    resources: list[str]


class StageOperationResult(BaseModel):
    result: LinearStageActionResult


ws_mgr = WebSocketConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attach state update hook to device controller to get websocket notification for state changes.
    sc.update_hook = WSDeviceStateUpdateSender(ws_mgr)
    # Start LinearStageController and corresponding threads
    sc.start()
    yield
    # Clean up resources, gracefully shut down LinearStageController
    sc.stop()
    # save hardware config on exit so that next time the user does not need to set up again.
    dump_hardware_config(hardware_config)


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
         'position',
         'absolute_position',
         'parameter',
         'ws(ws://)']
    return ServerResourceNames(resources=r)


@app.post("/")
async def stage_operation(operation: StageOperation,
                          token_data: Annotated[TokenData,
                                                Depends(validate_access_token)]
                          ) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    result = sc.stage_operation(operation=operation)
    return StageOperationResult(result=result)


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


@app.get("/position")
async def get_position(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> LogicalQuantitiy:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return LogicalQuantitiy(value=sc.position)


@app.post("/position")
async def set_position(target: LogicalQuantitiy,
                       token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_position(target.value)
    return StageOperationResult(result=op_result)


@app.get("/absolute_position")
async def get_absolute_position(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageDisplacement:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_absolute_position()


@app.post("/absolute_position")
async def set_absolute_position(operation: StageDisplacement,
                                token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_absolute_position(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.get("/parameter")
async def get_parameter(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageParameter:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.parameter


@app.get("/parameter/position")
async def get_parameter_position(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StagePositionParameter:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.parameter.position


@app.get("/parameter/velocity")
async def get_parameter_velocity(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageVelocityParameter:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.parameter.velocity


@app.post("/parameter/velocity")
async def set_parameter_velocity(operation: LogicalQuantitiy,
                                 token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_velocity(operation.value)
    return StageOperationResult(result=op_result)


@app.get("/parameter/physical_velocity")
async def get_parameter_physical_velocity(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageVelocity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_physical_velocity()


@app.post("/parameter/physical_velocity")
async def set_parameter_physical_velocity(operation: StageVelocity, token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_physical_velocity(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.get("/parameter/acceleration")
async def get_parameter_acceleration(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageAccelerationParameter:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.parameter.acceleration

@app.post("/parameter/acceleration")
async def set_parameter_acceleration(operation: LogicalQuantitiy,
                                 token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_acceleration(operation.value)
    return StageOperationResult(result=op_result)


@app.get("/parameter/physical_acceleration")
async def get_parameter_physical_acceleration(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageAcceleration:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_physical_acceleration()


@app.post("/parameter/physical_acceleration")
async def set_parameter_physical_acceleration(operation: StageAcceleration,
                                     token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_physical_acceleration(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    wsid = None
    try:
        wsid = await ws_mgr.connect(websocket)
        await ws_mgr.run(wsid)
    except (WebSocketDisconnect, ConnectionClosedOK) as e:
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
