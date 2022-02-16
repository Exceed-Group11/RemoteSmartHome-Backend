from pydantic import Basemodel

class Register(BaseModel):
    username: str
    password: str
    hardwareID: str
