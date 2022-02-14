from utils.database.hardware.hardware_command import HardwareCommand
from pymongo import MongoClient


class RemoteSmartHomeDatabase:
    def __init__(self):
        self.__mongo_client = MongoClient("mongodb://localhost:27017")
        self.__db = self.__mongo_client["SmartRemote"]
        self.__hardware = HardwareCommand(self.__db)

    @property
    def hardware(self) -> HardwareCommand:
        return self.__hardware
