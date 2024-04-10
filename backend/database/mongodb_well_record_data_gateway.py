from __future__ import annotations
from datetime import datetime, date
from typing import Callable

from pymongo import MongoClient

from backend.well_record import WellRecord
from backend.well_record.date_range import _default_daterange_parse_func

from .well_record_data_gateway import WellRecordDataGateway
from .mongodb_manager import MongoDBManager


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
    def _convert_date(d: datetime | None) -> date | None:
        """
        INTERNAL USE:

        Convert a ``datetime`` to a ``date`` object. If ``d`` is None,
        return None.
        :param d:
        :return:
        """
        if isinstance(d, datetime):
            return d.date()
        elif isinstance(d, date) or d is None:
            return d
        raise TypeError(
            "Passed object is neither `None` nor of type `datetime` or `date`."
        )

    @staticmethod
    def _well_record_to_dict(well_record: WellRecord) -> dict:
        """
        INTERNAL USE:
        Prep a ``WellRecord`` to be inserted into the MongoDB database,
        by converting it into a dict.

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

    @classmethod
    def _dict_to_well_record(
        cls,
        well_record_dict: dict,
        unpack_date_ranges_func: Callable = _default_daterange_parse_func,
    ) -> WellRecord:
        """
        INTERNAL USE:
        Map a returned MongoDB document to a ``WellRecord``.

        Specifically, convert a dict ``well_record_dict`` into a
        ``WellRecord``. The dict should contain the following keys and
        values (with types):

        - ``'_id'`` (str): The unique API number for this well.
            (Technically, this is the only required key in the dict.)

        - ``'well_name'`` (str): The name of the well.

        - ``'first_date'`` (``datetime``, ``date``, or ``None``): The
            first date of production records.

        - ``'last_date'`` (``datetime``, ``date``, or ``None``): The
            last date of production records.

        - ``'record_access_date'`` (``datetime``, ``date``, or
            ``None``): The date on which the production records were
            pulled from the official source.

        - ``'date_ranges'`` (``dict[str: list[str]]``): A dict of lists,
            keyed by the name of the category of the date range, with
            each list containing the respective date ranges, each in the
            form of a string (e.g., ``'2019-01-01::2020-12-31'``, the
            default format).

        Any other keys will be ignored.

        :param well_record_dict: The dict to convert to a ``WellRecord``
         (with keys and values as stated above).
        :param unpack_date_ranges_func: This function will take in each
         date range string in the lists stored at
         ``well_record_dict['date_ranges']`` and convert them to a
         ``DateRange`` object. The default function assumes that the
         date range strings are formatted as ``'2019-01-01::2020-12-31'``.
        :return: A new ``WellRecord`` with all date ranges registered.
        """
        wr = WellRecord(
            # our schema uses the API number as the id.
            api_num=well_record_dict.get("_id"),
            well_name=well_record_dict.get("well_name"),
            first_date=cls._convert_date(well_record_dict.get("first_date")),
            last_date=cls._convert_date(well_record_dict.get("last_date")),
            record_access_date=cls._convert_date(
                well_record_dict.get("record_access_date")
            ),
        )
        for category, date_ranges_raw in well_record_dict.get(
            "date_ranges", {}
        ).items():
            wr.register_empty_category(category)
            for dr_raw in date_ranges_raw:
                dr = unpack_date_ranges_func(dr_raw)
                wr.register_date_range(dr, category)
        return wr

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
            wr = self._dict_to_well_record(dct)
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


__all__ = [
    "MongoDBWellRecordDataGateway",
]
