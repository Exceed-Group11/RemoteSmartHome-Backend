from models.generate_remote_model import GenerateRemoteModel
from models.register_model import RegisterModel
from models.send_remote_action_model.state_model import StateModel
from models.signin_model import SignInModel
from utils.check_auth_token import verify_auth_token
from utils.database.remote_smart_home_database import RemoteSmartHomeDatabase
from utils.header_decoder import header_decoder
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, Header
from typing import Dict, Optional
import logging
import hashlib
import uuid
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
remote_collection = db["Remote"]
remote_smarthome_database = RemoteSmartHomeDatabase(mainLogger)
user_collection = db["Users"]
user_session = db["UserSession"]


# Main APIs

@app.get("/")
def health_api():
    return {
        "message": "success"
    }
# Frontend APIs


@app.post("/remote/{remote_id}/generate/")
def generate_remote(remote_id: str, remote_detail: GenerateRemoteModel, authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)

    # Get Default Remote Structure
    remote_structure = remote_smarthome_database.remote_structure.get_remote_structure_from_id(
        remote_id)
    list_remote_structure = list(remote_structure)
    if len(list_remote_structure) == 0:
        raise HTTPException(
            400, {
                "message": f"No remote structure with remoteId: {remote_id}"
            })

    user_remote = list_remote_structure.pop()
    structure_item = {}
    # Loop each button type
    for key, item in user_remote["structure"].items():
        if item["type"] == 1:
            # OnOff switch button type
            structure_item[key] = {
                "state": False
            }
        else:
            raise HTTPException(
                500, {
                    "message": "There was an error occurred while creating the remote. Contact backend team."
                })
    # Add remote name
    user_remote["remoteName"] = remote_detail.remoteName
    # Set the remote structure
    user_remote["structure"] = structure_item
    # Add userId field
    user_remote["userId"] = user_id

    # Find if user already has this remote.
    query_user_remote = {
        "userId": user_id, "remoteId": remote_id}
    user_remoteId = remote_collection.find(
        query_user_remote, {"_id": 0})
    list_user_remoteId = list(user_remoteId)
    if len(list_user_remoteId) != 0:
        raise HTTPException(400, {
            "message": f"This user already has Remote {remote_id}"
        })

    # Insert remote into the remote collection
    remote_collection.insert_one(user_remote)
    return {
        "message": "success"
    }


@app.delete("/remote/{remote_id}/")
def delete_remote(remote_id: str, authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)
    query_user_remote = {
        "remoteId": remote_id,
        "userId": user_id
    }
    query_result = remote_collection.find(query_user_remote, {"_id": 0})
    list_query_result = list(query_result)
    # No remote_id in user_id
    if len(list_query_result) == 0:
        raise HTTPException(404, {
            "message": f"couldn't find Remote {remote_id} "
        })

    remote_collection.delete_one(query_user_remote)
    # Response success
    return {
        "message": "success"
    }


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


@app.get("/remote/{remoteId}/")
def get_remote_status_1_by_1(remoteId: str, authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)
    query_user_remote = {
        "remoteId": remoteId,
        "userId": user_id
    }
    query_result = remote_collection.find(query_user_remote, {"_id": 0})
    list_query_result = list(query_result)
    # No remote_id in user_id
    if len(list_query_result) == 0:
        raise HTTPException(404, {
            "message": f"couldn't find Remote {remoteId}"
        })
    return list_query_result.pop()


@app.get("/remote/")
def show_all_status(authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)
    find_all = remote_collection.find({"userId": user_id}, {"_id": 0})
    return list(find_all)


@app.post("/remote/{remoteId}/button/{buttonId}/")
def send_remote_action_api(remoteId: str, buttonId: str, state: StateModel, authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)

    # Get user hardwareId
    user = remote_smarthome_database.user.get_user(
        {"userId": user_id})
    list_user = list(user)
    if len(list_user) != 1:
        raise HTTPException(
            404, {
                "message": "The userId is not found"
            })
    hardware_id = list_user[0]["hardwareId"]

    # Get Remote
    remote_result = remote_smarthome_database.remote.get_remote(
        {"userId": user_id, "remoteId": remoteId})
    if len(remote_result) != 1:
        raise HTTPException(
            404, {
                "message": "The remote is not found or found more than 1"
            })
    remote_user = remote_result[0]

    # Check if button is exists
    if remote_user["structure"].get(buttonId, "") == "":
        raise HTTPException(
            404, {
                "message": f"The inputted buttonId ({buttonId}) is not found for the remote {remoteId}"
            })
    # Check if the state in the database is the same thing that use want to interact
    if remote_user["structure"][buttonId]["state"] == state.state:
        raise HTTPException(
            400, {
                "message": f"The state of the button that you want to change is already {state.state}"
            })

    # Get Remote Structure
    remote_structure = remote_smarthome_database.remote_structure.get_remote_structure_from_id(
        remoteId)
    if len(remote_structure) != 1:
        raise HTTPException(
            404, {
                "message": "The remote structure is not found or found more than 1"
            })

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


@app.post("/user/register/")
def register_user(register: RegisterModel):
    # Check if username is already be used.
    result = remote_smarthome_database.user.get_user(
        {"username": register.username})
    if len(result) != 0:
        raise HTTPException(400, {
            "message": f"This username has already been used ({register.username})"
        })

    salt = generate_random_str(16)
    byte_salt = bytes(salt, "utf-8")
    hash_password = hashlib.pbkdf2_hmac(
        'sha256', register.password.encode('utf-8'), byte_salt, 100000
    )
    # Generate userID
    user_id = uuid.uuid4()

    user_object = {
        "userId": str(user_id),
        "username": register.username,
        "password": hash_password.hex(),
        "hardwareId": register.hardwareId,
        "salt": salt
    }
    user_collection.insert_one(user_object)
    return {
        "message": "success"
    }


@app.post("/user/signin/")
def sign_in(sign_in: SignInModel):
    # Get the user requested to sign in.
    find_user = remote_smarthome_database.user.get_user(
        {"username": sign_in.username})
    if len(find_user) != 1:
        raise HTTPException(401, {
            "message": "Username or Password is incorrected."
        })
    user_from_db: Dict = find_user.pop()
    # Find if the session is already existed.
    find_session = remote_smarthome_database.user_session.get_session(
        {"token": sign_in.token})

    if len(find_session) != 0:
        session: Dict = find_session.pop()
        # Check if the found session has the same userId has the one that want to sign in
        if session["userId"] == user_from_db["userId"]:
            # If yes, return 200 status code.
            return {
                "message": "User already signed in with this session id."
            }
        # If not, return 400 status code.
        raise HTTPException(400, {
            "message": "Some user is already signed in with this session id."
        })

    # Generate the hash password with the stored salt.
    check_password = hashlib.pbkdf2_hmac(
        'sha256', sign_in.password.encode(
            'utf-8'), bytes(user_from_db.get("salt", ""), "utf-8"), 100000
    ).hex()

    # Check if the generated hash password is the same as the one stored in the database.
    if (check_password != user_from_db.get("password", "")):
        raise HTTPException(401, {
            "message": "Username or Password is incorrected."
        })

    # Insert the new session.
    session_data = {
        "userId": user_from_db["userId"],
        "token": sign_in.token
    }
    user_session.insert_one(session_data)
    return {
        "message": "success"
    }


@app.post("/user/signout/")
def sign_out(authorization: Optional[str] = Header(None)):
    # Verify if the session is found
    verify_auth_token(remote_smarthome_database, authorization)
    # Get token from header again
    auth_token = header_decoder(authorization)

    remote_smarthome_database.user_session.delete_session(
        {"token": auth_token})
    return {
        "message": "success"
    }


@app.get("/user/")
def get_user_api(authorization: Optional[str] = Header(None)):
    # Get the userId based on the inputted token from header
    user_id = verify_auth_token(remote_smarthome_database, authorization)
    result = remote_smarthome_database.user.get_user({"userId": user_id})
    if len(result) != 1:
        raise HTTPException(
            404, "No userId associated with this session or found more than 1.")
    user_obj = result.pop()
    return {
        "hardwareId": user_obj.get("hardwareId", "UNKNOWN"),
        "userId": user_obj.get("userId", "UNKNOWN")
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
        raise HTTPException(401, {
            "message": "Unauthorized access."
        })
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
        raise HTTPException(401, {
            "message": "Unauthorized access."
        })
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
