import unittest
from datetime import date
from pathlib import Path

from backend.well_records.well_record import WellRecord
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)


class TestScraperWellDataCollector(unittest.TestCase):
    """Test scraping records for a well with reported production."""

    # Note: This well was P&A'd in 2021.
    api_num = "05-123-27133"
    well_name = "VILLAGE-11-16DU"
    html_mock_fp: Path = (
        Path(__file__).parent.parent.parent / r"_test_data/testpage_05-123-27133_html"
    )
    html_mock: str = None
    well_data: WellRecord = None

    @classmethod
    def setUpClass(cls):
        scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)
        cls.extracted_url = scraper.get_url(api_num=cls.api_num)
        cls.expected_url = r"https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code=123&api_seq_num=27133"
        # Mock the scraped raw HTML from a saved local copy.
        with open(Path(cls.html_mock_fp), mode="r") as file:
            cls.html_mock = "\n".join(file.readlines())
        cls.well_data = scraper.extract_well_record_from_html(
            cls.html_mock, cls.api_num
        )
        cls.ignore_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        cls.allow_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_BUT_SHUTIN_COUNTS
        )

    def test_get_url(self):
        self.assertEqual(self.expected_url, self.extracted_url)

    def test_scraped_well_name(self):
        self.assertEqual(self.well_name, self.well_data.well_name)

    def test_first_date(self):
        self.assertEqual(date(2009, 7, 1), self.well_data.first_date)

    def test_last_date(self):
        self.assertEqual(date(2021, 6, 30), self.well_data.last_date)

    def test_ignore_si_gaps_total(self):
        self.assertEqual(3, len(self.ignore_si_gaps))

    def test_ignore_si_gaps_start_date(self):
        gap_dr = self.ignore_si_gaps[1]
        self.assertEqual(date(2015, 12, 1), gap_dr.start_date)

    def test_ignore_si_gaps_end_date(self):
        gap_dr = self.ignore_si_gaps[1]
        self.assertEqual(date(2016, 3, 31), gap_dr.end_date)

    def test_allow_si_gaps_total(self):
        self.assertEqual(2, len(self.allow_si_gaps))

    def test_allow_si_gaps_start_date(self):
        gap_dr = self.allow_si_gaps[1]
        self.assertEqual(date(2021, 5, 1), gap_dr.start_date)

    def test_allow_si_gaps_end_date(self):
        gap_dr = self.allow_si_gaps[1]
        self.assertEqual(date(2021, 6, 30), gap_dr.end_date)


class TestScraperWellDataCollector_empty(unittest.TestCase):
    """Test scraping records for a well with no reported production."""

    # Note: This well never produced.
    api_num = "05-001-07729"
    well_name = "CHAMPLIN-15-27"
    html_mock_fp: Path = (
        Path(__file__).parent.parent.parent / r"_test_data/testpage_05-001-07729_html"
    )
    html_mock: str = None
    well_data: WellRecord = None

    @classmethod
    def setUpClass(cls):

        scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)
        cls.extracted_url = scraper.get_url(api_num=cls.api_num)
        cls.expected_url = r"https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code=001&api_seq_num=07729"
        # Mock the scraped raw HTML from a saved local copy.
        with open(Path(cls.html_mock_fp), mode="r") as file:
            cls.html_mock = "\n".join(file.readlines())
        cls.well_data = scraper.extract_well_record_from_html(
            cls.html_mock, cls.api_num
        )
        cls.ignore_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        cls.allow_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_BUT_SHUTIN_COUNTS
        )

    def test_get_url(self):
        self.assertEqual(self.expected_url, self.extracted_url)

    def test_first_date(self):
        self.assertIsNone(self.well_data.first_date)

    def test_last_date(self):
        self.assertIsNone(self.well_data.last_date)

    def test_ignore_si_gaps_total(self):
        self.assertEqual(0, len(self.ignore_si_gaps))

    def test_allow_si_gaps_total(self):
        self.assertEqual(0, len(self.allow_si_gaps))


if __name__ == "__main__":
    unittest.main()
