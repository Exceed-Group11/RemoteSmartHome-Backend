import logging
from pymongo import database


class DatabaseBase:
    def __init__(self, db, logger):
        self.__db: database = db
        self.__logger = logger

    @property
    def db(self) -> database:
        return self.__db

    @property
    def logger(self) -> logging:
        return self.__logger
