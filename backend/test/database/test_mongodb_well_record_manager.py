import unittest
from datetime import date

from pymongo import MongoClient

from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)
from backend.database.mongodb_well_record_manager import MongoDBWellRecordManager


TEST_DB_NAME = "testing_wrm"


def get_connection():
    return MongoClient("localhost", 27017)


def get_example_well_record():
    record = WellRecord(
        "99-123-45678",
        "Fake Well #1",
        first_date=date(2000, 1, 1),
        last_date=date(2024, 2, 1),
        record_access_date=date(2024, 4, 1),
    )
    record.register_empty_category(NO_PROD_IGNORE_SHUTIN)
    dr1 = DateRange(date(2010, 1, 1), date(2011, 12, 31))
    dr2 = DateRange(date(2013, 1, 1), date(2015, 12, 31))
    record.register_date_range(dr1, NO_PROD_IGNORE_SHUTIN)
    record.register_date_range(dr2, NO_PROD_IGNORE_SHUTIN)
    record.register_empty_category(NO_PROD_BUT_SHUTIN_COUNTS)
    record.register_date_range(dr1, NO_PROD_BUT_SHUTIN_COUNTS)
    record.register_date_range(dr2, NO_PROD_BUT_SHUTIN_COUNTS)
    return record


EXAMPLE_RECORD = get_example_well_record()


def drop_test_db(connection):
    connection.drop_database(TEST_DB_NAME)


class TestMongoDBWellRecordManager_insert(unittest.TestCase):

    def setUp(self):
        self.connection = get_connection()
        drop_test_db(self.connection)
        self.wrm = MongoDBWellRecordManager(
            self.connection,
            TEST_DB_NAME,
            well_records_collection_name="well_records",
        )
        return None

    def tearDown(self):
        drop_test_db(self.connection)
        return None

    def test_insert_well_record_count(self):
        self.wrm.insert_well_record(EXAMPLE_RECORD)
        self.assertEqual(1, self.wrm.well_records_collection.count_documents({}))


class TestMongoDBWellRecordManager_findSuccessful(unittest.TestCase):

    connection = get_connection()
    wrm = None
    example_record = EXAMPLE_RECORD
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_db(cls.connection)
        cls.wrm = MongoDBWellRecordManager(
            cls.connection,
            TEST_DB_NAME,
            well_records_collection_name="well_records",
        )
        cls.wrm.insert_well_record(cls.example_record)
        cls.recovered_record = cls.wrm.find_well_record(cls.example_record.api_num)

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_db(cls.connection)

    def test_was_found(self):
        self.assertIsNotNone(self.recovered_record)

    def test_attributes_match(self):
        attributes = [
            "api_num",
            "well_name",
            "first_date",
            "last_date",
            "record_access_date",
        ]
        for att in attributes:
            self.assertEqual(
                getattr(self.example_record, att), getattr(self.recovered_record, att)
            )

    def test_date_ranges_match(self):
        for category in (NO_PROD_IGNORE_SHUTIN, NO_PROD_BUT_SHUTIN_COUNTS):
            example_drs = EXAMPLE_RECORD.date_ranges_by_category(category)
            recovered_drs = self.recovered_record.date_ranges_by_category(category)
            self.assertEqual(
                len(example_drs),
                len(recovered_drs),
                f"Number of date ranges for category {category!r} do not match.",
            )
            zipped_date_ranges = zip(example_drs, recovered_drs)
            for i, (dr_source, dr_found) in enumerate(zipped_date_ranges):
                self.assertEqual(
                    dr_source.start_date,
                    dr_found.start_date,
                    f"Start date does not match.",
                )
                self.assertEqual(
                    dr_source.end_date, dr_found.end_date, "End date does not match."
                )


class TestMongoDBWellRecordManager_findUnsuccessful(unittest.TestCase):

    connection = get_connection()
    wrm = None
    example_record = EXAMPLE_RECORD
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_db(cls.connection)
        cls.wrm = MongoDBWellRecordManager(
            cls.connection,
            TEST_DB_NAME,
            well_records_collection_name="well_records",
        )
        cls.wrm.insert_well_record(cls.example_record)
        cls.recovered_record = cls.wrm.find_well_record("00-123-45678")

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_db(cls.connection)

    def test_was_not_found(self):
        self.assertIsNone(self.recovered_record)


class TestMongoDBWellRecordManager_update(unittest.TestCase):

    connection = get_connection()
    wrm = None
    example_record = EXAMPLE_RECORD
    updated_example_record = None
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_db(cls.connection)
        cls.wrm = MongoDBWellRecordManager(
            cls.connection,
            TEST_DB_NAME,
            well_records_collection_name="well_records",
        )
        cls.wrm.insert_well_record(cls.example_record)
        updated_example_record = get_example_well_record()
        # Get rid of one of the date ranges for NO_PROD_IGNORE_SHUTIN.
        updated_example_record.date_ranges[NO_PROD_IGNORE_SHUTIN].date_ranges.pop()
        cls.wrm.update_well_record(updated_example_record)
        cls.recovered_record = cls.wrm.find_well_record(cls.example_record.api_num)

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_db(cls.connection)

    def test_was_found(self):
        self.assertIsNotNone(self.recovered_record)

    def test_attributes_match(self):
        # These attributes were not modified.
        attributes = [
            "api_num",
            "well_name",
            "first_date",
            "last_date",
            "record_access_date",
        ]
        for att in attributes:
            self.assertEqual(
                getattr(self.example_record, att),
                getattr(self.recovered_record, att),
            )

    def test_date_ranges_match(self):

        # NO_PROD_BUT_SHUT_IN_COUNTS should be the same.
        for category in (NO_PROD_BUT_SHUTIN_COUNTS,):
            example_drs = self.example_record.date_ranges_by_category(category)
            recovered_drs = self.recovered_record.date_ranges_by_category(category)
            self.assertEqual(
                len(example_drs),
                len(recovered_drs),
                f"Number of date ranges for category {category!r} do not match.",
            )
            zipped_date_ranges = zip(example_drs, recovered_drs)
            for i, (dr_source, dr_found) in enumerate(zipped_date_ranges):
                self.assertEqual(
                    dr_source.start_date,
                    dr_found.start_date,
                    f"Start date does not match.",
                )
                self.assertEqual(
                    dr_source.end_date,
                    dr_found.end_date,
                    "End date does not match.",
                )

        # NO_PROD_IGNORE_SHUTIN should be different.
        for category in (NO_PROD_IGNORE_SHUTIN,):
            example_drs = self.example_record.date_ranges_by_category(category)
            recovered_drs = self.recovered_record.date_ranges_by_category(category)
            self.assertEqual(2, len(example_drs))
            self.assertEqual(1, len(recovered_drs))


class TestMongoDBWellRecordManager_delete(unittest.TestCase):

    connection = get_connection()
    wrm = None
    example_record = EXAMPLE_RECORD
    updated_example_record = None
    original_recovered_record = None
    final_recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_db(cls.connection)
        cls.wrm = MongoDBWellRecordManager(
            cls.connection,
            TEST_DB_NAME,
            well_records_collection_name="well_records",
        )
        cls.wrm.insert_well_record(cls.example_record)
        cls.original_recovered_record = cls.wrm.find_well_record(
            cls.example_record.api_num
        )
        cls.wrm.delete_well_record(cls.example_record.api_num)
        cls.final_recovered_record = cls.wrm.find_well_record(
            cls.example_record.api_num
        )

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_db(cls.connection)

    def test_original_was_found(self):
        self.assertIsNotNone(self.original_recovered_record)

    def test_deleted_was_not_found(self):
        self.assertIsNone(self.final_recovered_record)


if __name__ == "__main__":
    unittest.main()
