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

# Main APIs
@app.get("/")
def main_api_age():
    return {
        "message": "success"
    }
