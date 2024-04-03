from __future__ import annotations

import pymongo.database
from pymongo import MongoClient


class MongoDBManager:
    """
    Manager for a MongoDB database.
    """

    def __init__(self, connection: MongoClient, db_name: str, **kw) -> None:
        self.connection: MongoClient = connection
        self.db_name: str = db_name
        self.database: pymongo.database.Database = self.connection[self.db_name]


__all__ = [
    "MongoDBManager",
]
