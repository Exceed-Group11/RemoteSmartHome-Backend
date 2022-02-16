from re import search
from typing import Dict
from utils.database.base.database_base import DatabaseBase
from pymongo.collection import Collection


class UserCommand(DatabaseBase):
    def __init__(self, db, logger, hardware_collection_name="Users"):
        super().__init__(db, logger)
        self.__collection: Collection = self.db[hardware_collection_name]

    def get_user(self, searchObj: Dict):
        result = self.__collection.find(searchObj, {"_id": 0})
        list_result = list(result)
        self.logger.debug(f"Get user {searchObj}: {list_result}")
        return list_result
