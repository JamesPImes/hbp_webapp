from __future__ import annotations
import os
from datetime import datetime

from pymongo import MongoClient
import dotenv

from backend.well_records import WellRecord
from .well_record_data_gateway import WellRecordDataGateway
from .mongodb_manager import MongoDBManager
from .mongodb_loader import get_mongo_client_for_environment


dotenv.load_dotenv()


class MongoDBWellRecordDataGateway(MongoDBManager, WellRecordDataGateway):
    """
    Gateway for a MongoDB database, specifically handling a collection
    of individual well records.
    """

    def __init__(
        self, connection: MongoClient, db_name: str, well_records_collection_name: str
    ) -> None:
        super().__init__(connection, db_name)
        self.well_records_collection_name = well_records_collection_name
        self.well_records_collection = self.database[well_records_collection_name]

    @staticmethod
    def _well_record_to_dict(well_record: WellRecord) -> dict:
        """
        INTERNAL USE:
        Convert a ``WellRecord`` object into a dict, able to be inserted
        into the MongoDB database.

        :param well_record:
        :return:
        """
        _id = well_record.api_num
        if _id is None:
            raise ValueError("WellRecord must have .api_num.")
        d = {"_id": _id, "well_name": well_record.well_name}
        date_atts = ["first_date", "last_date", "record_access_date"]
        for att in date_atts:
            date_val = getattr(well_record, att)
            if date_val is not None:
                date_val = datetime(date_val.year, date_val.month, date_val.day)
            d[att] = date_val
        d["date_ranges"] = {}
        for dr_cat, dr_group in well_record.date_ranges.items():
            d["date_ranges"][dr_cat] = []
            for dr in dr_group:
                d["date_ranges"][dr_cat].append(str(dr))
        return d

    def insert(self, well_record: WellRecord, **kw) -> None:
        """
        Insert a new well record into the database.
        :param well_record: The ``WellRecord`` object to convert and
         store in the database.
        :return:
        """
        as_dict = self._well_record_to_dict(well_record)
        self.well_records_collection.insert_one(as_dict)
        return None

    def find(self, api_num: str, **kw) -> WellRecord | None:
        """
        Find the record for a well in the database based on its unique
        API number and convert it to a ``WellRecord`` object. If not
        found, return ``None``.
        """
        wr = None
        dct = self.well_records_collection.find_one({"_id": api_num})
        if dct is not None:
            dct["api_num"] = api_num
            wr = WellRecord.from_dict(dct)
        return wr

    def delete(self, api_num: str, **kw) -> None:
        """
        Delete the record for a well from the database based on its
        unique API number.
        :param api_num:
        :return:
        """
        self.well_records_collection.delete_one({"_id": api_num})
        return None

    def update(self, well_record: WellRecord, upsert=True) -> None:
        """
        Update the record for a well in the database. If not already in
        the database, it will be added if ``upsert=True`` (default
        behavior).
        :param well_record: The ``WellRecord`` object to convert and
         store in the database.
        :param upsert: If the well does not already exist in the
         database, ``upsert=True`` (the default) will cause it to be
         added.
        :return: None
        """
        as_dict = self._well_record_to_dict(well_record)
        new_vals = {}
        for k, v in as_dict.items():
            if k == "_id":
                continue
            new_vals = {"$set": {k: v}}
        self.well_records_collection.update_one(
            {"_id": as_dict["_id"]}, new_vals, upsert=upsert
        )
        return None


def get_well_record_gateway_for_environment(
    environment: str,
) -> MongoDBWellRecordDataGateway:
    """
    Get a ``MongoDBWellRecordDataGateway`` for the specified environment
    (``'PROD'``, ``'DEV'``, or ``'TEST'``; or another environment
    category specified in the ``.env`` file -- see ``.env.example`` for
    details).

    :param environment: ``'PROD'``, ``'DEV'``, ``'TEST'``, etc. (Will
     raise an ``EnvironmentError`` if the necessary environment
     variables for this environment are not specified in the ``.env``
     file.)
    :return: A configured ``MongoDBWellRecordDataGateway``.
    """

    connection = get_mongo_client_for_environment(environment)
    db_name = os.environ.get(f"DATABASE_NAME_{environment}")
    if db_name is None:
        raise EnvironmentError(
            f"Specify DATABASE_NAME_{environment} environment variable."
        )
    collection_name = os.environ.get(f"WELL_RECORDS_COLLECTION_{environment}")
    if collection_name is None:
        raise EnvironmentError(
            f"Specify WELL_RECORDS_COLLECTION_{environment} environment variable."
        )
    return MongoDBWellRecordDataGateway(
        connection,
        db_name=db_name,
        well_records_collection_name=collection_name,
    )


__all__ = [
    "MongoDBWellRecordDataGateway",
    "get_well_record_gateway_for_environment",
]