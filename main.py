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


# Main APIs
@app.post("{api_host}/remote/{user_id}/{remote_id}/generate/")
def generate_remote(remote_id: int, user_id: int, remote_type: int):
    query = remote_collection.find({"_id": 0, "userId": user_id})
    list_remote = list(query)
    #no remote found
    if len(list_remote) == 0:
        user_remote={
            "remoteId": remote_id,
            "userId": user_id,
            "structure": {
                "0": {
                    "type": remote_type,
                    "status": False
                }
            }
        }
    else:
        


    return {
        "message": f"Remote {remote_id} deleted"
    }
