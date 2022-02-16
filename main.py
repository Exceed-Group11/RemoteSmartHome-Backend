from utils.database.remote_smart_home_database import RemoteSmartHomeDatabase
from utils.header_decoder import header_decoder
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, Header
from typing import Optional
import logging
import hashlib
import os

# class usesr
from pydantic import BaseModel


class Register(BaseModel):
    username: str
    password: str
    hardwareId: str


# Main App
app = FastAPI()

# Allow CORS Policy
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the logging
mainLogger = logging.getLogger("RemoteSmarthome")
mainLogger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
mainLogger.addHandler(ch)

# Init Database Connection
client = MongoClient('mongodb://localhost', 27017)
db = client["SmartRemote"]
remote_smarthome_database = RemoteSmartHomeDatabase(mainLogger)
user_collection = db["Users"]

# Main APIs


@ app.get("/")
def health_api():
    return {
        "message": "success"
    }

# Frontend APIs


@app.get("/remote/{remoteId}/structure/")
def get_remote_structure(remoteId: str):
    if remoteId == "all":
        result = remote_smarthome_database.remote_structure.get_all_remote_structure()
    else:
        result = remote_smarthome_database.remote_structure.get_remote_structure_from_id(
            remoteId)

    # Verify result
    if len(result) == 0:
        raise HTTPException(404, {
            "message": "No remote structure found"
        })
    elif len(result) == 1:
        return result.pop()
    return result

# Hardware APIS


@ app.get("/hardware/commands/")
def get_commands_api(request: Request, authorization: Optional[str] = Header(None)):
    """This API is for the hardware to get the command
    to be transmited.

    Collection Name: HardwareCommands
    """
    # Decode the hardware id from request header
    try:
        hardware_id = header_decoder(authorization)
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")
    # Get the command based on the inputted hardware_id
    result = remote_smarthome_database.hardware.get_command(
        {"hardwareId": hardware_id})

    # Response 404 if the command was not found.
    if len(result) == 0:
        raise HTTPException(404, {
            "message": "No command found"
        })
    # Reponse the command only 1 command
    return result[0].to_dict()


@app.post("/hardware/command/{command_id}/ack/")
def send_ack_command_api(command_id: str, authorization: Optional[str] = Header(None)):
    # Decode the hardware id from request header
    try:
        hardware_id = header_decoder(authorization)
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")
    result = remote_smarthome_database.hardware.get_command(
        {"commandId": command_id, "hardwareId": hardware_id})
    if len(result) == 0:
        raise HTTPException(400, {
            "message": "No command found"
        })
    elif len(result) > 1:
        raise HTTPException(500, {
            "message": "We found two or more command sharing the same commandId. Please inform the backend team."
        })

    # Remove the command
    remote_smarthome_database.hardware.delete_command(
        {"commandId": command_id})
    return {
        "message": "success"
    }


@app.post("/user/register/")
def register_user(register: Register):
    salt = os.urandom(16)
    hash_password = hashlib.pbkdf2_hmac(
        'sha256', register.password.encode('utf-8'), salt, 100000
    )
    user_id = {
        "userId": "",
        "username": register.username,
        "password": hash_password,
        "hardwareId": register.hardwareId,
        "salt": salt
    }
    user_collection.insert_one(user_id)
    return {
        "message": "success"
    }
