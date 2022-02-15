from typing import Dict, List
from pymongo.collection import Collection
from utils.database.base.database_base import DatabaseBase


class UserSessionCommand(DatabaseBase):
    def __init__(self, db, logger, hardware_collection_name="UserSession"):
        super().__init__(db, logger)
        self.__collection: Collection = self.db[hardware_collection_name]

    def get_session(self, searchObj: Dict) -> List[Dict]:
        result = self.__collection.find(searchObj, {"_id": 0})
        self.logger.debug(f"Get Session {searchObj}: {result}")
        list_result = list(result)
        return list_result
