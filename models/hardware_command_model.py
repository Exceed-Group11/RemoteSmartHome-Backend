from multiprocessing.sharedctypes import Value
from typing import Dict, Optional

from models.base.base_model import ResponseModel


class HardwareCommandModel(ResponseModel):
    def __init__(self, commandId: str, value: Optional[int], hardwareId: Optional[str]):

        self.__commandId = commandId
        self.__value = value

    @property
    def commandId(self):
        return self.__commandId

    @property
    def value(self):
        return self.__value

    def to_dict(self):
        return {
            "commandId": self.__commandId,
            "value": self.__value
        }

    @staticmethod
    def from_dict(dict_data):
        if dict_data.get("commandId", "") == "":
            raise ValueError(
                f"No commandId found in the passed dict ({dict_data})")

        return HardwareCommandModel(commandId=dict_data["commandId"],
                                    value=dict_data.get("value", None),
                                    hardwareId=dict_data.get("hardwareId", None))
