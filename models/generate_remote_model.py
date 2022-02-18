from pydantic import BaseModel


class GenerateRemoteModel(BaseModel):
    remoteName: str
