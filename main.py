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
@app.delete("/remote/{remote_id}/")
def delete_remote(remote_id: str, authorization: Optional[str] = Header(None)):
    try:
        auth_token = header_decoder(authorization)
    except ValueError:
        raise HTTPException(401, "Unauthorized access.")

    query_token = {"token": auth_token}
    user_id = Usersession.find(query_token,{"_id": 0, "token": 0, "userId": 1})

    query_user_remote = {
      "remoteId": remote_id,
      "userId": user_id
    }
    query_result = remote_collection.find(query_user_remote, {"_id": 0})
    list_query_result = list(query_result)
    #No remote_id in user_id
    if len(list_query_result) == 0:
        return {
            "message": f"couldn't find Remote {remote_id} "
        }

    remote_collection.delete_one(query_result)
    return {
        "message": f"Remote {remote_id} deleted"
    }
