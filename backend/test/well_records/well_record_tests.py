import unittest
from datetime import date

from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange


class TestWellRecord(unittest.TestCase):

    def test_register_time_period(self):
        """Test that we can register two time periods."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1),
        )
        date_range_1 = DateRange.from_string(
            "2014-01-01::2015-02-01", category="test"
        )
        well_record.register_date_range(date_range_1)
        date_range_2 = DateRange.from_string(
            "2019-01-01::2020-12-01", category="test"
        )
        well_record.register_date_range(date_range_2)
        # 1 list contains 2 TimePeriod objects.
        number_of_lists = len(well_record.date_ranges)
        self.assertEqual(number_of_lists, 1)

    def test_date_ranges_by_category(self):
        """Test that we can recall date ranges by category."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1),
        )
        cat_name = "test"
        date_range_1 = DateRange.from_string(
            "2014-01-01::2015-02-01", category=cat_name
        )
        well_record.register_date_range(date_range_1)
        date_range_2 = DateRange.from_string(
            "2019-01-01::2020-12-01", category=cat_name
        )
        well_record.register_date_range(date_range_2)
        # Add to a different category.
        date_range_3 = DateRange.from_string(
            "2021-01-01::2022-12-01", category="other"
        )
        well_record.register_date_range(date_range_3)

        # The list for "test" category contains 2 TimePeriod objects.
        date_ranges_for_test_cat = well_record.date_ranges_by_category(category=cat_name)
        number_of_date_ranges = len(date_ranges_for_test_cat)
        self.assertEqual(number_of_date_ranges, 2)


if __name__ == "__main__":
    unittest.main()
