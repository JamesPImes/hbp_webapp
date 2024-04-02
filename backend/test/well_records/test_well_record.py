import unittest
from datetime import date, datetime

from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)


class TestWellRecord(unittest.TestCase):

    def test_register_date_range(self):
        """Test that we can register two date ranges."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1),
        )
        date_range_1 = DateRange(date(2014, 1, 1), date(2015, 2, 1))
        well_record.register_date_range(date_range_1, category="test")
        date_range_2 = DateRange(date(2019, 1, 1), date(2020, 12, 1))
        well_record.register_date_range(date_range_2, category="test")
        number_of_keys = len(well_record.date_ranges.keys())
        self.assertEqual(1, number_of_keys)

    def test_date_ranges_by_category(self):
        """Test that we can recall date ranges by category."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1),
        )
        cat_name = "test"
        date_range_1 = DateRange(date(2014, 1, 1), date(2015, 2, 1))
        well_record.register_date_range(date_range_1, cat_name)
        date_range_2 = DateRange(date(2019, 1, 1), date(2020, 12, 1))
        well_record.register_date_range(date_range_2, cat_name)
        # Add to a different category.
        date_range_3 = DateRange(date(2021, 1, 1), date(2022, 12, 1))
        well_record.register_date_range(date_range_3, category="other")

        # The DateRangeGroup for "test" category contains 2 TimePeriod objects.
        date_ranges_for_test_cat = well_record.date_ranges_by_category(
            category=cat_name
        )
        number_of_date_ranges = len(date_ranges_for_test_cat.date_ranges)
        self.assertEqual(2, number_of_date_ranges)


class TestWellRecord_fromDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        d = {
            "_id": "05-987-65432",
            "api_num": "05-987-65432",
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
        cls.well_record = WellRecord.from_dict(d)

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

if __name__ == "__main__":
    unittest.main()
