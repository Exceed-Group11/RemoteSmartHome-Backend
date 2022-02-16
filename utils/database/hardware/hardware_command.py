from typing import Dict, List
from models.hardware_command_model import HardwareCommandModel
from utils.database.base.database_base import DatabaseBase
from pymongo.collection import Collection


class HardwareCommand(DatabaseBase):

    def __init__(self, db, logger, hardware_collection_name="HardwareCommands"):
        super().__init__(db, logger)
        self.__collection: Collection = self.db[hardware_collection_name]

    def get_command(self, searchObject: Dict) -> List[HardwareCommandModel]:
        """Get all commands in the database based on the inputted
        hardwareId

        Args:
            searchObject (Dict): The search object.

        Returns:
            List[HardwareCommandModel]: List of the command that associalted with the inputted hardwareId
        """
        result = self.__collection.find(searchObject, {"_id": 0})
        list_result = list(result)
        self.logger.debug(f"Get Command Data - {list_result}")
        command_list = []
        # Convert everything to into the ResponseModel
        for item in list_result:
            hardware_model = HardwareCommandModel.from_dict(item)
            command_list.append(hardware_model)
        return command_list

    def delete_command(self, searchObject: Dict) -> None:
        """Delet the command that match the searchObject

        Args:
            searchObject (Dict): The search object.
        """
        self.__collection.delete_one(searchObject)
        self.logger.debug(f"Delete Command - {searchObject}")
        return

    def create_command(self, command: Dict) -> None:
        self.__collection.insert_one(command)
        self.logger.debug(f"Create command - {command}")
        return
