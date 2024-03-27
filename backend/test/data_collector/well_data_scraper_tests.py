import unittest
from datetime import date

from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)

COLORADO_CONFIG = {
    "prod_url_template": "https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code={0}&api_seq_num={1}",
    "date_col": "First of Month",
    "oil_prod_col": "Oil Produced",
    "gas_prod_col": "Gas Produced",
    "days_produced_col": "Days Produced",
    "status_col": "Well Status",
    "auth": None,
    "shutin_codes": ["SI"],
    "oil_prod_min": 0,
    "gas_prod_min": 0,
}


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        scraper = ScraperWellDataCollector(**COLORADO_CONFIG)

        # Note: This well was P&A'd in 2021, and we can expect that the
        # data will never be updated, since it no longer produces.
        api_num = "05-123-27133"
        well_name = "VILLAGE-11-16DU"
        kw = {"prod_url_components": ["123", "27133"]}
        cls.well_data = scraper.get_well_data(api_num, well_name, **kw)

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


if __name__ == "__main__":
    unittest.main()
