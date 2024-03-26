import unittest
from datetime import date

from backend.well_records.date_range import DateRange, DateRangeGroup


START_DATE = date(2014, 1, 1)
END_DATE = date(2015, 2, 1)
EXPECTED_DAYS = 397
EXPECTED_MONTHS = 14
DATE_RANGE_AS_STRING = "2014-01-01::2015-02-01"
CATEGORY = "TEST"


class TestDateRange(unittest.TestCase):

    def test_duration_in_days(self):
        date_range = DateRange(START_DATE, END_DATE, CATEGORY)
        self.assertEqual(date_range.duration_in_days(), EXPECTED_DAYS)

    def test_duration_in_months(self):
        date_range = DateRange(START_DATE, END_DATE, CATEGORY)
        self.assertEqual(date_range.duration_in_months(), EXPECTED_MONTHS)

    def test_from_string(self):
        date_range = DateRange.from_string(DATE_RANGE_AS_STRING, category=CATEGORY)
        self.assertEqual(date_range.duration_in_months(), EXPECTED_MONTHS)

    def test_is_contiguous_with(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2015, 2, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        self.assertTrue(tp1.is_contiguous_with(tp2))
        self.assertTrue(tp2.is_contiguous_with(tp1))

    def test_is_contiguous_with_false(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2015, 3, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        self.assertFalse(tp1.is_contiguous_with(tp2))
        self.assertFalse(tp2.is_contiguous_with(tp1))

    def test_encompasses(self):
        pass

    def test_merge_with(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        expected = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        result = tp1.merge_with(tp2)
        self.assertEqual(len(result), 1)
        merged_tp = result[0]
        self.assertEqual(merged_tp.start_date, expected.start_date)
        self.assertEqual(merged_tp.end_date, expected.end_date)

    def test_merge_with_no_overlap(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2016, 12, 1), end_date=date(2017, 5, 31), category=CATEGORY
        )
        result = tp1.merge_with(tp2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], tp1)
        self.assertEqual(result[1], tp2)

    def test_subtract_back(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        expected = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2014, 11, 30), category=CATEGORY
        )
        result = tp1.subtract(tp2)
        self.assertEqual(len(result), 1)
        subtracted_tp = result[0]
        self.assertEqual(subtracted_tp.start_date, expected.start_date)
        self.assertEqual(subtracted_tp.end_date, expected.end_date)

    def test_subtract_front(self):
        tp1 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        expected = DateRange(
            start_date=date(2015, 2, 1), end_date=date(2015, 5, 31), category=CATEGORY
        )
        result = tp1.subtract(tp2)
        self.assertEqual(len(result), 1)
        subtracted_tp = result[0]
        self.assertEqual(subtracted_tp.start_date, expected.start_date)
        self.assertEqual(subtracted_tp.end_date, expected.end_date)

    def test_subtract_all(self):
        tp1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2010, 1, 1), end_date=date(2020, 1, 1), category=CATEGORY
        )
        result = tp1.subtract(tp2)
        self.assertEqual(len(result), 0)

    def test_subtract_split(self):
        tp1 = DateRange(
            start_date=date(2010, 1, 1), end_date=date(2020, 12, 31), category=CATEGORY
        )
        tp2 = DateRange(
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31), category=CATEGORY
        )
        result = tp1.subtract(tp2)
        self.assertEqual(len(result), 2)
        subtracted_tp1 = result[0]
        self.assertEqual(subtracted_tp1.start_date, date(2010, 1, 1))
        self.assertEqual(subtracted_tp1.end_date, date(2014, 12, 31))
        subtracted_tp2 = result[1]
        self.assertEqual(subtracted_tp2.start_date, date(2016, 1, 1))
        self.assertEqual(subtracted_tp2.end_date, date(2020, 12, 31))


class TestDateRangeGroup(unittest.TestCase):
    def test_merge_all(self):
        dr1 = DateRange(start_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        dr2 = DateRange(start_date=date(2015, 1, 1), end_date=date(2017, 12, 31))
        dr3 = DateRange(start_date=date(2011, 1, 1), end_date=date(2012, 12, 31))
        drs = [dr1, dr2, dr3]
        group = DateRangeGroup(date_ranges=drs)
        group.merge_all()
        self.assertEqual(len(group.date_ranges), 2)

    def test_subtract_from_all(self):
        dr1 = DateRange(start_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        dr2 = DateRange(start_date=date(2015, 1, 1), end_date=date(2017, 12, 31))
        dr3 = DateRange(start_date=date(2011, 1, 1), end_date=date(2012, 12, 31))
        drs = [dr1, dr2, dr3]
        group = DateRangeGroup(date_ranges=drs)
        dr4 = DateRange(start_date=date(2010, 10, 1), end_date=date(2013, 12, 31))
        group.subtract_from_all(dr4)
        self.assertEqual(len(group.date_ranges), 2)


if __name__ == "__main__":
    unittest.main()
