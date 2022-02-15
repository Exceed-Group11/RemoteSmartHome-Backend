import logging
from utils.database.hardware.hardware_command import HardwareCommand
from utils.database.remote.remote_structure_command import RemoteStructureCommand
from pymongo import MongoClient


class RemoteSmartHomeDatabase:
    def __init__(self, logger: logging):
        self.__mongo_client = MongoClient("mongodb://localhost", 27017)
        self.__db = self.__mongo_client["SmartRemote"]
        self.__hardware = HardwareCommand(self.__db, logger)
        self.__remote_structure = RemoteStructureCommand(self.__db, logger)

    @property
    def hardware(self) -> HardwareCommand:
        return self.__hardware

    @property
    def remote_structure(self) -> RemoteStructureCommand:
        return self.__remote_structure
