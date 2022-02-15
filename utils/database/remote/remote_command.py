from typing import Dict, List
from pymongo.collection import Collection
from utils.database.base.database_base import DatabaseBase


class RemoteCommand(DatabaseBase):
    def __init__(self, db, logger, hardware_collection_name="Remote"):
        super().__init__(db, logger)
        self.__collection: Collection = self.db[hardware_collection_name]

    def get_remote(self, searchObj: Dict) -> List:
        result = self.__collection.find(searchObj, {"_id": 0})
        list_result = list(result)
        self.logger.debug(f"Get Remote {searchObj} - {list_result}")
        return list_result

    def update_remote(self, searchObj: Dict, updateObj: Dict) -> None:
        self.__collection.update_one(searchObj, updateObj)
        return
