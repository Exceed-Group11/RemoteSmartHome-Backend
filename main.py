from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel

# Main App
app = FastAPI()

# Allow CORS Policy
origins = [
    "*"
]
'''
{
  "remoteId": 1,
  "remoteName": "Example"
  "structure": {
     "0": {
         "type": 1,
         "value": {
            "0": "123143121",
            "1": "123123121"
         }
      }
  }
}
'''

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Remote(BaseModel):
  remoteId: int
  remoteName: str
  structure

# Init Database Connection
client = MongoClient('mongodb://localhost', 27017)
db = client["SmartRemote"]

# Main APIs
@app.post("/{{api_host}}/remote/:remoteId/generate/")
def main_api_age():
    return {
        "message": "success"
    }
