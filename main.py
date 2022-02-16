from models.send_remote_action_model.state_model import StateModel
from utils.database.remote_smart_home_database import RemoteSmartHomeDatabase
from utils.header_decoder import header_decoder
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, Header
from typing import Optional
import logging
import time

from utils.random_generator import generate_random_str


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


# Main APIs


@app.get("/")
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


@app.post("/remote/{remoteId}/button/{buttonId}")
def send_remote_action_api(remoteId: str, buttonId: str, state: StateModel, authorization: Optional[str] = Header(None)):
    # Decode the authorization token from request header
    try:
        auth_token = header_decoder(authorization)
        user_result = remote_smarthome_database.user_session.get_session(
            {"token": auth_token})
        if len(user_result) != 1:
            raise ValueError()
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")
    # Get User's hardware id
    user_id = user_result[0]["userId"]
    user = remote_smarthome_database.user.get_user(
        {"userId": user_id})
    list_user = list(user)
    if len(list_user) != 1:
        raise HTTPException(
            404, "The userId is not found")
    hardware_id = list_user[0]["hardwareId"]

    # Get Remote
    remote_result = remote_smarthome_database.remote.get_remote(
        {"userId": user_id, "remoteId": remoteId})
    if len(remote_result) != 1:
        raise HTTPException(
            404, "The remote is not found or found more than 1")
    remote_user = remote_result[0]

    # Check if button is exists
    if remote_user["structure"].get(buttonId, "") == "":
        raise HTTPException(
            404, f"The inputted buttonId ({buttonId}) is not found for the remote {remoteId}")
    # Check if the state in the database is the same thing that use want to interact
    if remote_user["structure"][buttonId]["state"] == state.state:
        raise HTTPException(
            400, f"The state of the button that you want to change is already {state.state}")

    # Get Remote Structure
    remote_structure = remote_smarthome_database.remote_structure.get_remote_structure_from_id(
        remoteId)
    if len(remote_structure) != 1:
        raise HTTPException(
            404, "The remote structure is not found or found more than 1")

    # Generate the command_id
    command_id = generate_random_str(10)
    # Generate the command
    remote_smarthome_database.hardware.create_command({
        "commandId": command_id,
        "hardwareId":  hardware_id,
        "value": remote_structure[0]["structure"][buttonId]["value"][str(int(state.state))]
    })

    # Check if command has been removed (Ack by hardware)
    count = 0
    while True:
        # Check if timeout
        if count >= 15:
            # Delete the command
            remote_smarthome_database.hardware.delete_command(
                {"commandId": command_id})
            # response 504
            raise HTTPException(
                504, {"message": "The targered hardware doesn't response in time"})

        result = remote_smarthome_database.hardware.get_command(
            {"commandId": command_id})
        if len(result) == 0:
            break
        count += 1
        time.sleep(1)

    # Update the button state in backend

    new_structure = remote_user["structure"]
    new_structure[buttonId]["state"] = state.state
    remote_smarthome_database.remote.update_remote({
        "remoteId": remoteId,
        "userId": user_id
    },
        {
            "$set": {
                "structure": new_structure
            }
    }
    )

    return {
        "message": "success"
    }

# Hardware APIS


@app.get("/hardware/commands/")
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

@app.get("/remote/")
def show_all_status():

@app.post("/user/siginin/")
def sign_in(user: Register):
    find_user = user.collection.find({user.username})
    salt = os.urandom(16)
    hash_password = hahslib.pbkdf2_hmac('sha256',user.password('utf-8'),salt,100000)
    if find_user.pasword == hash_password :
        print("Login Success")
    else:
        print("Wrong Try again")
    return  {}
            
