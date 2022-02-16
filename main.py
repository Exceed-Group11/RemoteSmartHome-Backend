from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

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

# Init Database Connection
client = MongoClient('mongodb://localhost', 27017)
db = client["SmartRemote"]
remote_collection = db["Remote"]

# generate_remote API
@app.post("/remote/{remote_id}/generate/")
def generate_remote(remote_id: str, remote_id: str,authorization: Optional[str] = Header(None)):
     try:
        auth_token = header_decoder(authorization)
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")

    query_token = {"token": auth_token}
    user_id = Usersession.find(query,{"_id": 0, "token": 0, "userId": 1})
    #find user remote 
    query_user_remote = {"userId": user_id}
    user_remoteId = remote_collection.find(query_user_remote,{"_id": 0, "userId": 0, "remoteId":1 , "structure": 0})
    list_user_remoteId = list(user_remoteId)
    #if remote_id is found in remote_collection
    for user_remote_Id in list_user_remoteId:
        if user_remote_Id == remote_id:
            return{
                "message": f"This user has Remote {remote_id} already "
            }

    user_remote={
        "remoteId": remote_id,
        "userId": user_id,
        "structure": {
            "0": {
                "type": 1
                "status": False
                "value":{
                    "0": "1234"
                    "1": "5678"
                }
            }
        }
    }
    remote_collection.insert_one(user_remote)
    return {
        "message": f"Remote {remote_id} generated"
    }
