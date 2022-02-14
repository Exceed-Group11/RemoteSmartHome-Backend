from operator import itemgetter
from typing import Dict, List
from models.hardware_command_model import HardwareCommandModel
from utils.database.base.database_base import DatabaseBase
from pymongo import collection


class HardwareCommand(DatabaseBase):

    def __init__(self, db, hardware_collection_name="HardwareCommands"):
        super().__init__(db)
        self.__collection: collection = self.db[hardware_collection_name]

    def get_command(self, hardwareId: str) -> List[HardwareCommandModel]:
        result = self.__collection.find(
            {"hardwareId": hardwareId}, {"_id": 0})
        list_result = list(result)
        command_list = []
        for item in list_result:
            hardware_model = HardwareCommandModel.from_dict(item)
            command_list.append(hardware_model)
        return command_list
