import unittest
from datetime import datetime, date

from mongomock import MongoClient

from backend.well_records import (
    WellRecord,
    DateRange,
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)
from backend.database import MongoDBWellRecordDataGateway


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


# Use a mongomock.MongoClient instead of (real) pymongo.MongoClient.
MOCK_CONNECTION = MongoClient("localhost", 27017)
# MongoDBWellRecordManager handles interactions with the database.
GATEWAY = MongoDBWellRecordDataGateway(
    MOCK_CONNECTION, "hbp_webapp_test", well_records_collection_name="well_records_test"
)
EXAMPLE_RECORD = get_example_well_record()


def drop_test_collection():
    GATEWAY.database.drop_collection(GATEWAY.well_records_collection_name)


class TestMongoDBWellRecordManager_insert(unittest.TestCase):

    def setUp(self):
        drop_test_collection()
        return None

    def tearDown(self):
        drop_test_collection()
        return None

    def test_insert_well_record_count(self):
        GATEWAY.insert(EXAMPLE_RECORD)
        self.assertEqual(1, GATEWAY.well_records_collection.count_documents({}))


class TestMongoDBWellRecordManager_findSuccessful(unittest.TestCase):

    example_record = EXAMPLE_RECORD
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_collection()
        GATEWAY.insert(cls.example_record)
        cls.recovered_record = GATEWAY.find(cls.example_record.api_num)

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_collection()

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

    example_record = EXAMPLE_RECORD
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_collection()
        GATEWAY.insert(cls.example_record)
        cls.recovered_record = GATEWAY.find("00-123-45678")

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_collection()

    def test_was_not_found(self):
        self.assertIsNone(self.recovered_record)


class TestMongoDBWellRecordManager_update(unittest.TestCase):

    example_record = EXAMPLE_RECORD
    updated_example_record = None
    recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_collection()
        GATEWAY.insert(cls.example_record)
        updated_example_record = get_example_well_record()
        # Get rid of one of the date ranges for NO_PROD_IGNORE_SHUTIN.
        updated_example_record.date_ranges[NO_PROD_IGNORE_SHUTIN].date_ranges.pop()
        GATEWAY.update(updated_example_record)
        cls.recovered_record = GATEWAY.find(cls.example_record.api_num)

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_collection()

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

    example_record = EXAMPLE_RECORD
    updated_example_record = None
    original_recovered_record = None
    final_recovered_record = None

    @classmethod
    def setUpClass(cls):
        drop_test_collection()
        GATEWAY.insert(cls.example_record)
        cls.original_recovered_record = GATEWAY.find(cls.example_record.api_num)
        GATEWAY.delete(cls.example_record.api_num)
        cls.final_recovered_record = GATEWAY.find(cls.example_record.api_num)

    @classmethod
    def tearDownClass(cls) -> None:
        drop_test_collection()

    def test_original_was_found(self):
        self.assertIsNotNone(self.original_recovered_record)

    def test_deleted_was_not_found(self):
        self.assertIsNone(self.final_recovered_record)


class TestMongoDBWellRecordManager_map_to_well_record(unittest.TestCase):
    """Test mapping a Mongo document to a ``WellRecord`` object."""

    as_mongo_schema: dict = None
    well_record: WellRecord = None

    @classmethod
    def setUpClass(cls):
        # A dict, as pulled from the mongo database.
        cls.as_mongo_schema = {
            "_id": "05-987-65432",
            "well_name": "Test Well #1",
            "first_date": datetime(2020, 12, 1),
            "last_date": datetime(2024, 1, 1),
            "record_access_date": datetime(2024, 3, 31),
            "date_ranges": {
                NO_PROD_IGNORE_SHUTIN: [
                    "2021-01-01::2022-12-31",
                    "2023-01-01::2023-07-31",
                ],
                NO_PROD_BUT_SHUTIN_COUNTS: [],
            },
        }
        cls.well_record = MongoDBWellRecordDataGateway._dict_to_well_record(
            cls.as_mongo_schema
        )

    def test_api_num(self):
        self.assertEqual(self.as_mongo_schema["_id"], self.well_record.api_num)

    def test_well_name(self):
        self.assertEqual(self.as_mongo_schema["well_name"], self.well_record.well_name)

    def test_first_date(self):
        self.assertEqual(date(2020, 12, 1), self.well_record.first_date)

    def test_last_date(self):
        self.assertEqual(date(2024, 1, 1), self.well_record.last_date)

    def test_record_access_date(self):
        self.assertEqual(date(2024, 3, 31), self.well_record.record_access_date)

    def test_date_ranges_by_category_noprod(self):
        """Test that we can recall date ranges by category."""
        date_ranges_for_test_cat = self.well_record.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        number_of_date_ranges = len(date_ranges_for_test_cat.date_ranges)
        self.assertEqual(2, number_of_date_ranges)

    def test_date_ranges_by_category_noprod_daterange1_start_date(self):
        """Test that we can recall date ranges by category."""
        date_ranges_for_test_cat = self.well_record.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        dr1 = date_ranges_for_test_cat[0]
        self.assertEqual(date(2021, 1, 1), dr1.start_date)

    def test_date_ranges_by_category_noprod_daterange1_end_date(self):
        """Test that we can recall date ranges by category."""
        date_ranges_for_test_cat = self.well_record.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        dr1 = date_ranges_for_test_cat[0]
        self.assertEqual(date(2022, 12, 31), dr1.end_date)

    def test_date_ranges_by_category_shutin(self):
        """Test that we can recall date ranges by category."""
        date_ranges_for_test_cat = self.well_record.date_ranges_by_category(
            category=NO_PROD_BUT_SHUTIN_COUNTS
        )
        number_of_date_ranges = len(date_ranges_for_test_cat.date_ranges)
        self.assertEqual(0, number_of_date_ranges)


class TestMongoDBWellRecordManager_well_record_to_dict(unittest.TestCase):
    """Test preparing a ``WellRecord`` object for the Mongo schema."""

    expected: dict = None
    well_record: WellRecord = None
    as_mongo_schema: dict = None

    @classmethod
    def setUpClass(cls):
        cls.well_record = WellRecord(
            api_num="05-987-65432",
            well_name="Test Well #1",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1),
            record_access_date=datetime(2024, 3, 31),
        )
        cls.well_record.register_empty_category(NO_PROD_IGNORE_SHUTIN)
        cls.well_record.register_date_range(
            date_range=DateRange(
                start_date=date(2021, 1, 1), end_date=date(2022, 12, 31)
            ),
            category=NO_PROD_IGNORE_SHUTIN,
        )
        cls.well_record.register_date_range(
            date_range=DateRange(
                start_date=date(2023, 1, 1), end_date=date(2023, 7, 31)
            ),
            category=NO_PROD_IGNORE_SHUTIN,
        )
        cls.well_record.register_empty_category(NO_PROD_BUT_SHUTIN_COUNTS)

        # Equivalent record in the schema used by the database.
        cls.expected = {
            "_id": "05-987-65432",  # api_num becomes _id
            "well_name": "Test Well #1",
            "first_date": datetime(2020, 12, 1),
            "last_date": datetime(2024, 1, 1),
            "record_access_date": datetime(2024, 3, 31),
            "date_ranges": {
                NO_PROD_IGNORE_SHUTIN: [
                    "2021-01-01::2022-12-31",
                    "2023-01-01::2023-07-31",
                ],
                NO_PROD_BUT_SHUTIN_COUNTS: [],
            },
        }
        cls.as_mongo_schema = MongoDBWellRecordDataGateway._well_record_to_dict(
            cls.well_record
        )

    def test_date_ranges_by_category_noprod(self):
        """Test date ranges by category."""
        date_ranges = self.as_mongo_schema["date_ranges"][NO_PROD_IGNORE_SHUTIN]
        number_of_date_ranges = len(date_ranges)
        self.assertEqual(2, number_of_date_ranges)

    def test_date_ranges_by_category_noprod_daterange_string1(self):
        """Test that we can recall date ranges by category."""
        dr1_str_found = self.as_mongo_schema["date_ranges"][NO_PROD_IGNORE_SHUTIN][0]
        dr1_str_expected = self.as_mongo_schema["date_ranges"][NO_PROD_IGNORE_SHUTIN][0]
        self.assertEqual(dr1_str_expected, dr1_str_found)

    def test_date_ranges_by_category_shutin(self):
        """Test that we can recall date ranges by category."""
        date_ranges = self.as_mongo_schema["date_ranges"][NO_PROD_BUT_SHUTIN_COUNTS]
        number_of_date_ranges = len(date_ranges)
        self.assertEqual(0, number_of_date_ranges)

    def test_id(self):
        self.assertEqual(self.as_mongo_schema["_id"], self.expected["_id"])

    def test_well_name(self):
        self.assertEqual(self.as_mongo_schema["well_name"], self.expected["well_name"])

    def test_first_date(self):
        self.assertEqual(self.as_mongo_schema["first_date"], self.expected["first_date"])

    def test_last_date(self):
        self.assertEqual(self.as_mongo_schema["last_date"], self.expected["last_date"])

    def test_record_access_date(self):
        self.assertEqual(self.as_mongo_schema["record_access_date"], self.expected["record_access_date"])

    def test_date_ranges(self):
        self.assertEqual(self.as_mongo_schema["date_ranges"], self.expected["date_ranges"])


if __name__ == "__main__":
    unittest.main()
