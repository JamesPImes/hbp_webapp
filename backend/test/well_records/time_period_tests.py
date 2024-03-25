import unittest
from datetime import date

from backend.well_records.time_period import TimePeriod


START_DATE = date(2014, 1, 1)
END_DATE = date(2015, 2, 1)
EXPECTED_DAYS = 396
EXPECTED_MONTHS = 13
DATE_RANGE_AS_STRING = "2014-01-01::2015-02-01"
CATEGORY = "TEST"


class TestTimePeriod(unittest.TestCase):

    def test_duration_in_days(self):
        time_period = TimePeriod(START_DATE, END_DATE, CATEGORY)
        self.assertEqual(time_period.duration_in_days(), EXPECTED_DAYS)

    def test_duration_in_months(self):
        time_period = TimePeriod(START_DATE, END_DATE, CATEGORY)
        self.assertEqual(time_period.duration_in_months(), EXPECTED_MONTHS)

    def test_from_string(self):
        time_period = TimePeriod.from_string(DATE_RANGE_AS_STRING, category=CATEGORY)
        self.assertEqual(time_period.duration_in_months(), EXPECTED_MONTHS)


if __name__ == "__main__":
    unittest.main()
