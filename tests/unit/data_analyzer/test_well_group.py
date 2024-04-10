import unittest
from datetime import date

from backend.data_analyzer import WellGroup
from backend.well_record import WellRecord, DateRange


class TestWellGroup(unittest.TestCase):

    def test_add_well_record(self):
        wg = WellGroup()
        wr1 = WellRecord(api_num="05-123-45678", well_name="test well #1")
        wr2 = WellRecord(api_num="05-123-98765", well_name="test well #2")
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)
        self.assertEqual(len(wg.well_records), 2)

    def test_find_first_date(self):
        wg = WellGroup()
        expected_first_date = date(2001, 1, 1)
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=expected_first_date,
            last_date=date(2020, 5, 1),
        )
        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=date(2019, 11, 1),
            last_date=date(2023, 5, 1),
        )
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)
        self.assertEqual(expected_first_date, wg.find_first_date())

    def test_find_first_date_none(self):
        wg = WellGroup()
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=None,
            last_date=None,
        )
        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=None,
            last_date=None,
        )
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)
        self.assertEqual(None, wg.find_first_date())

    def test_find_last_date(self):
        wg = WellGroup()
        expected_last_date = date(2023, 5, 1)
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=date(2001, 1, 1),
            last_date=date(2020, 5, 1),
        )
        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=date(2019, 11, 1),
            last_date=expected_last_date,
        )
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)
        self.assertEqual(expected_last_date, wg.find_last_date())

    def test_find_last_date_none(self):
        wg = WellGroup()
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=None,
            last_date=None,
        )
        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=None,
            last_date=None,
        )
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)
        self.assertEqual(None, wg.find_last_date())


class TestWellGroup_gaps(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=date(2001, 1, 1),
            last_date=date(2020, 5, 31),
        )
        dr1 = DateRange(start_date=date(2002, 1, 1), end_date=date(2003, 12, 31))
        wr1.register_date_range(dr1, category="test")
        ignore_dr = DateRange(start_date=date(2002, 4, 1), end_date=date(2003, 7, 31))
        wr1.register_date_range(ignore_dr, category="ignore")

        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=date(2002, 1, 1),
            last_date=date(2023, 5, 1),
        )
        dr2 = DateRange(start_date=date(2002, 5, 1), end_date=date(2004, 11, 30))
        wr2.register_date_range(dr2, category="test")

        wg = WellGroup()
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)

        cls.gaps = wg.find_gaps(category="test")
        cls.dr_expected = DateRange(
            start_date=date(2002, 5, 1), end_date=date(2003, 12, 31)
        )

    def test_find_gaps_number_found(self):
        self.assertEqual(len(self.gaps), 1)

    def test_find_gaps_start_date(self):
        gap = self.gaps[0]
        self.assertEqual(self.dr_expected.start_date, gap.start_date)

    def test_find_gaps_end_date(self):
        gap = self.gaps[0]
        self.assertEqual(self.dr_expected.end_date, gap.end_date)


class TestWellGroup_gapsWithEmpty(unittest.TestCase):
    """Test a well group with one well that had no production reported."""

    @classmethod
    def setUpClass(cls):
        wr1 = WellRecord(
            api_num="05-123-45678",
            well_name="test well #1",
            first_date=date(2001, 1, 1),
            last_date=date(2020, 5, 31),
        )
        dr1 = DateRange(start_date=date(2002, 1, 1), end_date=date(2003, 12, 31))
        wr1.register_date_range(dr1, category="test")
        ignore_dr = DateRange(start_date=date(2002, 4, 1), end_date=date(2003, 7, 31))
        wr1.register_date_range(ignore_dr, category="ignore")

        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=None,
            last_date=None,
        )
        wr2.register_empty_category("test")

        wg = WellGroup()
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)

        cls.gaps = wg.find_gaps(category="test")
        cls.dr_expected = DateRange(
            start_date=date(2002, 1, 1), end_date=date(2003, 12, 31)
        )

    def test_find_gaps_number_found(self):
        self.assertEqual(len(self.gaps), 1)

    def test_find_gaps_start_date(self):
        gap = self.gaps[0]
        self.assertEqual(self.dr_expected.start_date, gap.start_date)

    def test_find_gaps_end_date(self):
        gap = self.gaps[0]
        self.assertEqual(self.dr_expected.end_date, gap.end_date)


if __name__ == "__main__":
    unittest.main()
