import unittest
from datetime import date

from backend.well_records.time_period import TimePeriod


START_DATE = date(2014, 1, 1)
END_DATE = date(2015, 2, 1)
EXPECTED_DAYS = 397
EXPECTED_MONTHS = 14
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

    def test_is_contiguous_with(self):
        tp1 = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = TimePeriod(
            start_date=date(2015, 2, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        self.assertTrue(tp1.is_contiguous_with(tp2))
        self.assertTrue(tp2.is_contiguous_with(tp1))

    def test_is_contiguous_with_false(self):
        tp1 = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = TimePeriod(
            start_date=date(2015, 3, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        self.assertFalse(tp1.is_contiguous_with(tp2))
        self.assertFalse(tp2.is_contiguous_with(tp1))

    def test_merge_with(self):
        tp1 = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = TimePeriod(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        expected = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        result = tp1.merge_with(tp2)
        self.assertEqual(result.start_date, expected.start_date)
        self.assertEqual(result.end_date, expected.end_date)

    def test_subtract_out(self):
        tp1 = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = TimePeriod(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        expected = TimePeriod(
            start_date=date(2014, 1, 1), end_date=date(2014, 11, 30), category=CATEGORY
        )
        result = tp1.subtract_out(tp2)
        self.assertEqual(result.start_date, expected.start_date)
        self.assertEqual(result.end_date, expected.end_date)


if __name__ == "__main__":
    unittest.main()
