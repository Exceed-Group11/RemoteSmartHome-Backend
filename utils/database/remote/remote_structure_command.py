from typing import Dict, List
from utils.database.base.database_base import DatabaseBase
from pymongo.collection import Collection
import logging


class RemoteStructureCommand(DatabaseBase):

    def __init__(self, db, logger, hardware_collection_name="RemoteStructures"):
        super().__init__(db, logger)
        self.__collection: Collection = self.db[hardware_collection_name]

    def get_all_remote_structure(self) -> List[Dict]:
        result = self.__collection.find({}, {"_id": 0})
        list_result = list(result)
        self.logger.debug(f"Get All remote Structure - {list_result}")
        return list_result

    def get_remote_structure_from_id(self, remote_id: str) -> Dict:
        result = self.__collection.find(
            {"remoteId": remote_id}, {"_id": 0})
        list_result = list(result)
        self.logger.debug(
            f"Get remote Structure ID:{remote_id} - {list_result}")
        return list_result
