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
@app.delete("/remote/{remoteId}/")
def delete_remote(remote_id: str, authorization: Optional[str] = Header(None)):
    try:
        auth_token = header_decoder(authorization)
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")

    query_token = {"token": auth_token}
    user_id = Usersession.find(query,{"_id": 0, "token": 0, "userId": 1})
    
    query = {
      "remoteId": remote_id,
      "userId": user_id
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
