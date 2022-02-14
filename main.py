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
@app.delete("/{api_host}/remote/{remote_id}}/")
def delete_remote(remote_id: int):
    query_remoteID = {
      "remoteID": remote_id
      }
    query_result = remote_collection.find(query_remoteID, {"_id": 0})
    remote_list = list(query_result)
    if len(list_query_toilet) != 1:
        raise HTTPException(400, {
            "message": "The remote id was not found or there were 2 or more remotes found."
        })
    remote_collection.delete_one(query_remoteID)
    return {
        "message": f"Remote {remote_id} deleted"
    }
