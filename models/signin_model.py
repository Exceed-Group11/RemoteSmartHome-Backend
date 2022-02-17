from pydantic import BaseModel


class SignInModel(BaseModel):
    username: str
    password: str
    token: str
