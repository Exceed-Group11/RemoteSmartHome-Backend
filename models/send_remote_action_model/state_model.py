from pydantic import BaseModel


class StateModel(BaseModel):
    state: bool
