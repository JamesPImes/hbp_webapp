import unittest
from datetime import date

from backend.well_records.date_range import DateRange, DateRangeGroup


class TestDateRange_basic(unittest.TestCase):

    START_DATE = date(2014, 1, 1)
    END_DATE = date(2015, 2, 1)
    EXPECTED_DAYS = 397
    EXPECTED_MONTHS = 14

    @classmethod
    def setUpClass(cls):
        cls.date_range = DateRange(cls.START_DATE, cls.END_DATE)

    def test_duration_in_days(self):
        self.assertEqual(self.EXPECTED_DAYS, self.date_range.duration_in_days())

    def test_duration_in_months(self):
        self.assertEqual(self.EXPECTED_MONTHS, self.date_range.duration_in_months())


class TestDateRange_comparisonsContiguous(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Date ranges 1 and 2 are contiguous, but 1 and 3 are not.
        cls.dr1 = DateRange(start_date=date(2014, 1, 1), end_date=date(2015, 1, 31))
        cls.dr2 = DateRange(start_date=date(2015, 2, 1), end_date=date(2015, 5, 31))
        cls.dr3 = DateRange(start_date=date(2015, 3, 1), end_date=date(2015, 5, 31))

    def test_is_contiguous_with_a_to_b(self):
        self.assertTrue(self.dr1.is_contiguous_with(self.dr2))

    def test_is_contiguous_with_b_to_a(self):
        self.assertTrue(self.dr2.is_contiguous_with(self.dr1))

    def test_is_contiguous_with_a_to_b_false(self):
        self.assertFalse(self.dr1.is_contiguous_with(self.dr3))

    def test_is_contiguous_with_b_to_a_false(self):
        self.assertFalse(self.dr3.is_contiguous_with(self.dr1))


class TestDateRange_comparissonsEncompasses(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr1 = DateRange(start_date=date(2013, 1, 1), end_date=date(2015, 12, 31))
        cls.dr2 = DateRange(start_date=date(2014, 1, 1), end_date=date(2014, 12, 31))

    def test_encompasses_true(self):
        self.assertTrue(self.dr1.encompasses(self.dr2))

    def test_encompasses_false(self):
        self.assertFalse(self.dr2.encompasses(self.dr1))


class TestDateRange_merge(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.merge_dr1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31)
        )
        cls.merge_dr2 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31)
        )
        cls.merge_expected = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 5, 31)
        )

        cls.no_merge_dr1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31)
        )
        cls.no_merge_dr2 = DateRange(
            start_date=date(2016, 12, 1), end_date=date(2017, 5, 31)
        )

    def test_merge_with_len(self):
        result = self.merge_dr1.merge_with(self.merge_dr2)
        self.assertEqual(1, len(result))

    def test_merge_with_start_date(self):
        result = self.merge_dr1.merge_with(self.merge_dr2)
        merged_dr = result[0]
        self.assertEqual(self.merge_expected.start_date, merged_dr.start_date)
        self.assertEqual(self.merge_expected.end_date, merged_dr.end_date)

    def test_merge_with_no_overlap_len(self):
        result = self.no_merge_dr1.merge_with(self.no_merge_dr2)
        self.assertEqual(2, len(result))

    def test_merge_with_no_overlap_same_first(self):
        result = self.no_merge_dr1.merge_with(self.no_merge_dr2)
        self.assertEqual(self.no_merge_dr1, result[0])

    def test_merge_with_no_overlap_same_second(self):
        result = self.no_merge_dr1.merge_with(self.no_merge_dr2)
        self.assertEqual(self.no_merge_dr2, result[1])


class TestDateRange_subtract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Subtracting back_dr2 trims the back end of back_dr1.
        cls.back_dr1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31)
        )
        cls.back_dr2 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31)
        )
        cls.back_expected = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2014, 11, 30)
        )

        # Subtracting back_dr2 trims the front end of back_dr1.
        cls.front_dr1 = DateRange(
            start_date=date(2014, 12, 1), end_date=date(2015, 5, 31)
        )
        cls.front_dr2 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31)
        )
        cls.front_expected = DateRange(
            start_date=date(2015, 2, 1), end_date=date(2015, 5, 31)
        )

        # Subtracting entire_dr2 from trims the entirety of entire_dr1.
        cls.entire_dr1 = DateRange(
            start_date=date(2014, 1, 1), end_date=date(2015, 1, 31)
        )
        cls.entire_dr2 = DateRange(
            start_date=date(2010, 1, 1), end_date=date(2020, 1, 1)
        )

        # Subtracting split_dr2 splits split_dr1 in two parts.
        cls.split_dr1 = DateRange(
            start_date=date(2010, 1, 1), end_date=date(2020, 12, 31)
        )
        cls.split_dr2 = DateRange(
            start_date=date(2015, 1, 1), end_date=date(2015, 12, 31)
        )

        cls.split_expected_1 = DateRange(date(2010, 1, 1), date(2014, 12, 31))
        cls.split_expected_2 = DateRange(date(2016, 1, 1), date(2020, 12, 31))

    def test_subtract_back_len(self):
        result = self.back_dr1.subtract(self.back_dr2)
        self.assertEqual(1, len(result))

    def test_subtract_back_start_date(self):
        result = self.back_dr1.subtract(self.back_dr2)
        subtracted_dr = result[0]
        self.assertEqual(self.back_expected.start_date, subtracted_dr.start_date)
        self.assertEqual(self.back_expected.end_date, subtracted_dr.end_date)

    def test_subtract_back_end_date(self):
        result = self.back_dr1.subtract(self.back_dr2)
        subtracted_dr = result[0]
        self.assertEqual(self.back_expected.end_date, subtracted_dr.end_date)

    def test_subtract_front_len(self):
        result = self.front_dr1.subtract(self.front_dr2)
        self.assertEqual(1, len(result))

    def test_subtract_front_start_date(self):
        result = self.front_dr1.subtract(self.front_dr2)
        subtracted_dr = result[0]
        self.assertEqual(self.front_expected.start_date, subtracted_dr.start_date)

    def test_subtract_front_end_date(self):
        result = self.front_dr1.subtract(self.front_dr2)
        subtracted_dr = result[0]
        self.assertEqual(self.front_expected.end_date, subtracted_dr.end_date)

    def test_subtract_entire(self):
        result = self.entire_dr1.subtract(self.entire_dr2)
        self.assertEqual(0, len(result))

    def test_subtract_split_len(self):
        result = self.split_dr1.subtract(self.split_dr2)
        self.assertEqual(2, len(result))

    def test_subtract_split_first_start_date(self):
        result = self.split_dr1.subtract(self.split_dr2)
        subtracted_dr1 = result[0]
        self.assertEqual(self.split_expected_1.start_date, subtracted_dr1.start_date)

    def test_subtract_split_first_end_date(self):
        result = self.split_dr1.subtract(self.split_dr2)
        subtracted_dr1 = result[0]
        self.assertEqual(self.split_expected_1.end_date, subtracted_dr1.end_date)

    def test_subtract_split_second_start_date(self):
        result = self.split_dr1.subtract(self.split_dr2)
        subtracted_dr2 = result[1]
        self.assertEqual(self.split_expected_2.start_date, subtracted_dr2.start_date)

    def test_subtract_split_second_end_date(self):
        result = self.split_dr1.subtract(self.split_dr2)
        subtracted_dr2 = result[1]
        self.assertEqual(self.split_expected_2.end_date, subtracted_dr2.end_date)


class TestDateRange_overlap(unittest.TestCase):

    def test_find_overlap(self):
        dr1 = DateRange(date(2010, 1, 1), date(2011, 12, 31))
        dr2 = DateRange(date(2011, 1, 1), date(2012, 12, 31))
        overlap = dr1.find_overlap(dr2)
        self.assertEqual(365, overlap.duration_in_days())


class TestDateRangeGroup_merge_subtract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr1 = DateRange(start_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        cls.dr2 = DateRange(start_date=date(2015, 1, 1), end_date=date(2017, 12, 31))
        cls.dr3 = DateRange(start_date=date(2011, 1, 1), end_date=date(2012, 12, 31))
        cls.dr4 = DateRange(start_date=date(2010, 10, 1), end_date=date(2013, 12, 31))

    def test_merge_all(self):
        group = DateRangeGroup(date_ranges=[self.dr1, self.dr2, self.dr3])
        group.merge_all()
        self.assertEqual(2, len(group.date_ranges))

    def test_subtract_from_all(self):
        group = DateRangeGroup(date_ranges=[self.dr1, self.dr2, self.dr3])
        group.subtract_from_all(self.dr4)
        self.assertEqual(2, len(group.date_ranges))

class TestDateRangeGroup_overlaps(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
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
        cls.overlap_group = group1.find_all_overlaps(group2)

    def test_find_all_overlaps_len(self):
        self.assertEqual(4, len(self.overlap_group.date_ranges))

    def test_find_all_overlaps_first_start_date(self):
        self.assertEqual(date(2011, 1, 1), self.overlap_group.date_ranges[0].start_date)

    def test_find_all_overlaps_first_end_date(self):
        self.assertEqual(date(2011, 12, 31), self.overlap_group.date_ranges[0].end_date)

    def test_find_all_overlaps_durations(self):
        for dr in self.overlap_group.date_ranges:
            self.assertEqual(365, dr.duration_in_days())


if __name__ == "__main__":
    unittest.main()
