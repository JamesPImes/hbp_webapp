import unittest
from datetime import date

from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)


class TestScraperWellDataCollector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)

        # Note: This well was P&A'd in 2021, and we can expect that the
        # data will never be updated, since it no longer produces.
        api_num = "05-123-27133"
        well_name = "VILLAGE-11-16DU"
        cls.well_data = scraper.get_well_data(api_num, well_name)

        cls.ignore_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        cls.allow_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_BUT_SHUTIN_COUNTS
        )

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

    @classmethod
    def setUpClass(cls):
        scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)

        # Note: This well never produced.
        api_num = "05-001-07729"
        well_name = "CHAMPLIN #15-27"
        cls.well_data = scraper.get_well_data(api_num, well_name)

        cls.ignore_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_IGNORE_SHUTIN
        )
        cls.allow_si_gaps = cls.well_data.date_ranges_by_category(
            category=NO_PROD_BUT_SHUTIN_COUNTS
        )

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
