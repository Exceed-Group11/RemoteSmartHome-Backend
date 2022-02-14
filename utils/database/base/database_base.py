from pymongo import database


class DatabaseBase:
    def __init__(self, db):
        self.__db: database = db

    @property
    def db(self) -> database:
        return self.__db
