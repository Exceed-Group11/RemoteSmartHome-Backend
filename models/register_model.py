from pydantic import BaseModel


class RegisterModel(BaseModel):
    username: str
    password: str
    hardwareID: str
