# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

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
from pydantic import BaseModel, ValidationError
# external package
from serial_helper import SerialManager, SerialMocker
# this package
from .linear_stage import LinearStageController, LinearStageActionResult
from .server_config import server_config, UserAccessLevel
from .hardware_config import hardware_config, StageDisplacement, StagePosition, StageVelocity, StageAcceleration, StageOperation
from .hardware_config import dump_config_to_file as dump_hardware_config
from .auth import try_authenticate, create_access_token, validate_access_token, Token, TokenData, AccessLevelException, check_access_level, check_access_level_ws
from .ws import WebSocketConnectionManager


class ServerStatusReport(BaseModel):
    status: str


class ServerResourceNames(BaseModel):
    resources: list[str]


class StageOperationResult(BaseModel):
    result: LinearStageActionResult


# create LinearStageController that all threads shares according to config.
serial_config = hardware_config.serial
ser_mgr = SerialManager(
    serial_config.port, baudrate=serial_config.baudrate, timeout=serial_config.timeout)

# ----- TEMPORARY FOR TESTING
IS_TESTING = True
if IS_TESTING:
    # mut borrow ser_mgr, replace Serial with Mocked Serial
    # mocked response according to our protocol
    response_map = {
        b"AUTOHOME\r": b"OK\r",
    }

    def r(b: bytes) -> bytes:
        if b'MOVEABS' in b:
            return b'OK\r'
        return b''
    ser_mgr.ser = SerialMocker(
        serial_config.port, baudrate=serial_config.baudrate, timeout=serial_config.timeout,
        response_map=response_map, response_generator=r)
# ===== END TEMPORARY FOR TESTING

sc = LinearStageController(ser_mgr, hardware_config)
ws_mgr = WebSocketConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
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
         'velocity',
         'acceleration',
         'ws(ws://)']
    return ServerResourceNames(resources=r)


@app.post("/")
async def stage_operation(operation: StageOperation, token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    r = sc.stage_operation(operation)
    return StageOperationResult(result=r)


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
async def get_position(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StagePosition:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.position


@app.post("/position")
async def set_position(operation: StagePosition,
                       token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.move_to_position(operation.value)
    return StageOperationResult(result=op_result)


@app.get("/absolute_position")
async def get_absolute_position(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageDisplacement:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.get_absolute_position()


@app.post("/absolute_position")
async def set_absolute_position(operation: StageDisplacement,
                                token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.move_to_absolute_position(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.get("/velocity")
async def get_velocity(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageVelocity:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.stage.velocity


@app.post("/velocity")
async def set_velocity(operation: StageVelocity,
                       token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_velocity(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.get("/acceleration")
async def get_acceleration(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageAcceleration:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return sc.config.stage.acceleration


@app.post("/acceleration")
async def set_acceleration(operation: StageAcceleration,
                           token_data: Annotated[TokenData, Depends(validate_access_token)]) -> StageOperationResult:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    op_result = sc.set_acceleration(operation.value, operation.unit)
    return StageOperationResult(result=op_result)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    try:
        await ws_mgr.connect(websocket)
        while True:
            # receive a command, validate the command and execute the command.
            data = await websocket.receive_json()
            op = StageOperation(**data)
            # check user priviledge
            check_access_level_ws(
                ws_mgr.active_connections.get(websocket).access_level,
                UserAccessLevel.readonly)
            # perform operation
            op_result = sc.stage_operation(op)
            # tell operating client result of operation.
            response_data = {}
            response_data["result"] = op_result.value
            if "id" in data:
                response_data["id"] = data["id"]
            await websocket.send_json(response_data)
            # because the device is a shared resource of all clients, broadcast the newest state to all clients.
            await ws_mgr.broadcast(jsonable_encoder(op))
    except WebSocketDisconnect:
        # user disconnected from client side.
        pass
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
        # clear websocket stored in manager as well as its auth info.
        ws_mgr.disconnect(websocket)
