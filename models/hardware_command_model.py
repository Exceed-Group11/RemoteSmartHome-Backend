from multiprocessing.sharedctypes import Value
from typing import Optional

from models.base.base_model import ResponseModel


class HardwareCommandModel(ResponseModel):
    def __init__(self, command_id: str, value: Optional[int], hardware_id: Optional[str]):

        self.__command_id = command_id
        self.__value = value
        self.__hardware_id = hardware_id

    @property
    def commandId(self):
        return self.__command_id

    @property
    def hardware_id(self):
        return self.__hardware_id

    @property
    def value(self):
        return self.__value

    @property
    def value(self):
        return self.__value

    def to_dict(self):
        return {
            "commandId": self.__command_id,
            "value": self.__value,
            "hardwareId": self.__hardware_id
        }

    @staticmethod
    def from_dict(dict_data):
        if dict_data.get("commandId", "") == "":
            raise ValueError(
                f"No commandId found in the passed dict ({dict_data})")

        return HardwareCommandModel(command_id=dict_data["commandId"],
                                    value=dict_data.get("value", None),
                                    hardware_id=dict_data.get("hardwareId", None))
