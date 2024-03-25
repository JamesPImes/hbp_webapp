
import unittest
from datetime import date

from backend.well_records.well_record import WellRecord
from backend.well_records.time_period import TimePeriod


class TestWellRecord(unittest.TestCase):

    def test_register_time_period(self):
        """Test that we can register two time periods."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1)
        )
        time_period_1 = TimePeriod.from_string("2014-01-01::2015-02-01", category="test")
        well_record.register_time_period(time_period_1)
        time_period_2 = TimePeriod.from_string("2019-01-01::2020-12-01", category="test")
        well_record.register_time_period(time_period_2)
        # 1 list contains 2 TimePeriod objects.
        number_of_lists = len(well_record.time_periods)
        self.assertEqual(number_of_lists, 1)

    def test_time_periods_by_cat(self):
        """Test that we can recall time periods by category."""
        well_record = WellRecord(
            api_num="05-0123-45678",
            well_name="test well name",
            first_date=date(2020, 12, 1),
            last_date=date(2024, 1, 1)
        )
        cat_name = "test"
        time_period_1 = TimePeriod.from_string("2014-01-01::2015-02-01", category=cat_name)
        well_record.register_time_period(time_period_1)
        time_period_2 = TimePeriod.from_string("2019-01-01::2020-12-01", category=cat_name)
        well_record.register_time_period(time_period_2)
        # Add to a different category.
        time_period_3 = TimePeriod.from_string("2021-01-01::2022-12-01", category="other")
        well_record.register_time_period(time_period_3)

        # The list for "test" category contains 2 TimePeriod objects.
        time_periods_for_test_cat = well_record.time_periods_by_cat(category=cat_name)
        number_of_time_periods = len(time_periods_for_test_cat)
        self.assertEqual(number_of_time_periods, 2)


if __name__ == '__main__':
    unittest.main()
