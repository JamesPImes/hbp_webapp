import unittest
from datetime import date

from backend.well_records.date_range import DateRange, DateRangeGroup


START_DATE = date(2014, 1, 1)
END_DATE = date(2015, 2, 1)
EXPECTED_DAYS = 397
EXPECTED_MONTHS = 14
DATE_RANGE_AS_STRING = "2014-01-01::2015-02-01"


class TestDateRange(unittest.TestCase):

    def test_duration_in_days(self):
        date_range = DateRange(START_DATE, END_DATE)
        self.assertEqual(date_range.duration_in_days(), EXPECTED_DAYS)

    def test_duration_in_months(self):
        date_range = DateRange(START_DATE, END_DATE)
        self.assertEqual(date_range.duration_in_months(), EXPECTED_MONTHS)

    def test_from_string(self):
        date_range = DateRange.from_string(DATE_RANGE_AS_STRING)
        self.assertEqual(date_range.duration_in_months(), EXPECTED_MONTHS)

    def test_is_contiguous_with(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2015, 2, 1), end_date=date(2015, 5, 31))
        self.assertTrue(dr1.is_contiguous_with(dr2))
        self.assertTrue(dr2.is_contiguous_with(dr1))

    def test_is_contiguous_with_false(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2015, 3, 1), end_date=date(2015, 5, 31))
        self.assertFalse(dr1.is_contiguous_with(dr2))
        self.assertFalse(dr2.is_contiguous_with(dr1))

    def test_encompasses(self):
        pass

    def test_merge_with(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2014, 12, 1), end_date=date(2015, 5, 31))
        expected = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 5, 31))
        result = dr1.merge_with(dr2)
        self.assertEqual(len(result), 1)
        merged_dr = result[0]
        self.assertEqual(merged_dr.start_date, expected.start_date)
        self.assertEqual(merged_dr.end_date, expected.end_date)

    def test_merge_with_no_overlap(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2016, 12, 1), end_date=date(2017, 5, 31))
        result = dr1.merge_with(dr2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], dr1)
        self.assertEqual(result[1], dr2)

    def test_subtract_back(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2014, 12, 1), end_date=date(2015, 5, 31))
        expected = DateRange(start_date=date(2014, 1, 1), end_date=date(2014, 11, 30))
        result = dr1.subtract(dr2)
        self.assertEqual(len(result), 1)
        subtracted_dr = result[0]
        self.assertEqual(subtracted_dr.start_date, expected.start_date)
        self.assertEqual(subtracted_dr.end_date, expected.end_date)

    def test_subtract_front(self):
        dr1 = DateRange(start_date=date(2014, 12, 1), end_date=date(2015, 5, 31))
        dr2 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        expected = DateRange(start_date=date(2015, 2, 1), end_date=date(2015, 5, 31))
        result = dr1.subtract(dr2)
        self.assertEqual(len(result), 1)
        subtracted_dr = result[0]
        self.assertEqual(subtracted_dr.start_date, expected.start_date)
        self.assertEqual(subtracted_dr.end_date, expected.end_date)

    def test_subtract_all(self):
        dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        dr2 = DateRange(start_date=date(2010, 1, 1), end_date=date(2020, 1, 1))
        result = dr1.subtract(dr2)
        self.assertEqual(len(result), 0)

    def test_subtract_split(self):
        dr1 = DateRange(start_date=date(2010, 1, 1), end_date=date(2020, 12, 31))
        dr2 = DateRange(start_date=date(2015, 1, 1), end_date=date(2015, 12, 31))
        result = dr1.subtract(dr2)
        self.assertEqual(len(result), 2)
        subtracted_dr1 = result[0]
        self.assertEqual(subtracted_dr1.start_date, date(2010, 1, 1))
        self.assertEqual(subtracted_dr1.end_date, date(2014, 12, 31))
        subtracted_dr2 = result[1]
        self.assertEqual(subtracted_dr2.start_date, date(2016, 1, 1))
        self.assertEqual(subtracted_dr2.end_date, date(2020, 12, 31))

    def test_find_overlap(self):
        dr1 = DateRange(date(2010, 1, 1), date(2011, 12, 31))
        dr2 = DateRange(date(2011, 1, 1), date(2012, 12, 31))
        overlap = dr1.find_overlap(dr2)
        self.assertEqual(overlap.duration_in_days(), 365)


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

    def test_find_all_overlaps(self):
        dr1 = DateRange(date(2010, 1, 1), date(2011, 12, 31))
        dr2 = DateRange(date(2014, 1, 1), date(2015, 12, 31))
        dr3 = DateRange(date(2018, 1, 1), date(2019, 12, 31))
        dr4 = DateRange(date(2022, 1, 1), date(2023, 12, 31))

        dr5 = DateRange(date(2011, 1, 1), date(2012, 12, 31))
        dr6 = DateRange(date(2015, 1, 1), date(2016, 12, 31))
        dr7 = DateRange(date(2019, 1, 1), date(2020, 12, 31))
        dr8 = DateRange(date(2023, 1, 1), date(2024, 12, 31))

        group1 = DateRangeGroup([dr1, dr2, dr3, dr4])
        group2 = DateRangeGroup([dr5, dr6, dr7, dr8])

        overlap_group = group1.find_all_overlaps(group2)
        print(overlap_group)
        self.assertEqual(len(overlap_group.date_ranges), 4)
        self.assertEqual(overlap_group.date_ranges[0].start_date, date(2011, 1, 1))
        self.assertEqual(overlap_group.date_ranges[0].end_date, date(2011, 12, 31))
        for dr in overlap_group.date_ranges:
            self.assertEqual(dr.duration_in_days(), 365)


if __name__ == "__main__":
    unittest.main()
