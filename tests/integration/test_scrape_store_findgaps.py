"""
Integration test for the following:
- Scrape the production records for 2 wells from local copies of
    Colorado's public records.
- Store the records to the database.
- Add the records to a ``WellGroup`` object to find collective
    production gaps across the two wells.
"""

import unittest
from pathlib import Path

from mongomock import MongoClient

from backend.data_analyzer import WellGroup
from backend.data_collector import ScraperWellDataCollector
from backend.data_collector.state_configs import COLORADO_CONFIG
from backend.well_record import NO_PROD_IGNORE_SHUTIN
from backend.database import MongoDBWellRecordDataGateway


# Use a mongomock.MongoClient instead of (real) pymongo.MongoClient.
MOCK_CONNECTION = MongoClient("localhost", 27017)
# MongoDBWellRecordDataGateway handles interactions with the database.
GATEWAY = MongoDBWellRecordDataGateway(
    MOCK_CONNECTION, "hbp_webapp_test", well_records_collection_name="well_records_test"
)


def drop_test_collection():
    GATEWAY.database.drop_collection(GATEWAY.well_records_collection_name)


class TestScrapeAndStore(unittest.TestCase):

    well_group = WellGroup()
    scraper: ScraperWellDataCollector = None

    # Note: API #05-123-27133 has 3 gaps (not counting shut-in periods);
    # and API #05-001-07729 has never produced. We should find 3 gaps.
    # And we may expect that the production records for these wells will
    # never be modified.
    api_num1 = "05-123-27133"
    well_name1 = "VILLAGE-11-16DU"
    html_mock_fp1: Path = (
        Path(__file__).parent.parent / r"_test_data/testpage_05-123-27133_html"
    )
    html_mock1: str = None

    api_num2 = "05-001-07729"
    well_name2 = "CHAMPLIN #15-27"
    html_mock_fp2: Path = (
        Path(__file__).parent.parent / r"_test_data/testpage_05-001-07729_html"
    )
    html_mock2: str = None

    @classmethod
    def setUpClass(cls):
        drop_test_collection()
        cls.scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)
        # Note: API #05-123-27133 has 3 gaps (not counting shut-in periods);
        # and API #05-001-07729 has never produced. We should find 3 gaps.
        # And we may expect that the production records for these wells will
        # never be modified.

        with open(Path(cls.html_mock_fp1), mode="r") as file:
            cls.html_mock1 = "\n".join(file.readlines())

        with open(Path(cls.html_mock_fp2), mode="r") as file:
            cls.html_mock2 = "\n".join(file.readlines())

        api_nums_to_mock_html = {
            "05-123-27133": cls.html_mock1,
            "05-001-07729": cls.html_mock2,
        }
        cls.well_group = WellGroup()
        for i, (api_num, html_mock) in enumerate(
            api_nums_to_mock_html.items(), start=1
        ):
            well_record = cls.scraper.extract_well_record_from_html(
                html_mock, api_num, f"Test Well #{i}"
            )
            # Add well record to the WellGroup.
            cls.well_group.well_records.append(well_record)
            # Insert well record into the database.
            GATEWAY.insert(well_record)
        return None

    @classmethod
    def tearDownClass(cls):
        drop_test_collection()

    def test_well_record_count(self):
        self.assertEqual(2, len(self.well_group.well_records))

    def test_database(self):
        self.assertEqual(2, GATEWAY.well_records_collection.count_documents({}))

    def test_find_gaps(self):
        ignore_si_gaps = self.well_group.find_gaps(category=NO_PROD_IGNORE_SHUTIN)
        self.assertEqual(3, len(ignore_si_gaps))


if __name__ == "__main__":
    unittest.main()
