"""
Integration test for the following:
- Scrape the production records for 2 wells from Colorado's public
    records.
- Store the records to the database.
- Add the records to a ``WellGroup`` object to find collective
    production gaps across the two wells.
"""

import unittest

from pymongo import MongoClient

from backend.data_analyzer.well_group import WellGroup
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG
from backend.well_records.standard_categories import NO_PROD_IGNORE_SHUTIN
from backend.database.mongodb_well_record_manager import MongoDBWellRecordManager

TEST_DB_NAME = "testing_integration"


def get_connection():
    return MongoClient("localhost", 27017)


def drop_test_db(connection):
    connection.drop_database(TEST_DB_NAME)


class TestScrapeAndStore(unittest.TestCase):

    connection = get_connection()
    wrm: MongoDBWellRecordManager = None
    well_group = WellGroup()
    scraper: ScraperWellDataCollector = None

    @classmethod
    def setUpClass(cls):
        drop_test_db(cls.connection)
        cls.wrm = MongoDBWellRecordManager(cls.connection, TEST_DB_NAME, "well_records")
        cls.scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)
        # Note: API #05-123-27133 has 3 gaps (not counting shut-in periods);
        # and API #05-001-07729 has never produced. We should find 3 gaps.
        # And we may expect that the production records for these wells will
        # never be modified.
        api_nums = [
            "05-123-27133",
            "05-001-07729",
        ]
        cls.well_group = WellGroup()
        for i, api_num in enumerate(api_nums, start=1):
            well_record = cls.scraper.get_well_data(api_num, f"Test Well #{i}")
            # Add well record to the WellGroup.
            cls.well_group.well_records.append(well_record)
            # Insert well record into the database.
            cls.wrm.insert_well_record(well_record)
        return None

    @classmethod
    def tearDownClass(cls):
        drop_test_db(cls.connection)

    def test_well_record_count(self):
        self.assertEqual(2, len(self.well_group.well_records))

    def test_database(self):
        self.assertEqual(2, self.wrm.well_records_collection.count_documents({}))

    def test_find_gaps(self):
        ignore_si_gaps = self.well_group.find_gaps(category=NO_PROD_IGNORE_SHUTIN)
        self.assertEqual(3, len(ignore_si_gaps))


if __name__ == "__main__":
    unittest.main()
