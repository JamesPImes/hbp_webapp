import unittest
from datetime import date

from backend.data_analyzer.well_group import WellGroup
from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange


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
        self.assertEqual(wg.find_first_date(), expected_first_date)

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
        self.assertEqual(wg.find_first_date(), None)

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
        self.assertEqual(wg.find_last_date(), expected_last_date)

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
        self.assertEqual(wg.find_last_date(), None)

    def test_find_gaps(self):
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

        gaps = wg.find_gaps(category="test")
        dr_expected = DateRange(start_date=date(2002, 5, 1), end_date=date(2003, 12, 31))
        # Only 1 gap remains.
        self.assertEqual(
            len(gaps),
            1,
            f"Expected 1 gap to remain for category 'test'; found {len(gaps)}.",
        )
        gap = gaps[0]
        # Start dates match.
        self.assertEqual(
            gap.start_date,
            dr_expected.start_date,
            f"Expected start date of {dr_expected.start_date}; found {gap.start_date}.",
        )
        # End dates match.
        self.assertEqual(
            gap.end_date,
            dr_expected.end_date,
            f"Expected end date of {dr_expected.end_date}; found {gap.end_date}.",
        )


if __name__ == "__main__":
    unittest.main()
