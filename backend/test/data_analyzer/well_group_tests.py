import unittest
from datetime import date

from backend.data_analyzer.well_group import WellGroup
from backend.well_records.well_record import WellRecord
from backend.well_records.time_period import TimePeriod


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
        tp1 = TimePeriod(
            start_date=date(2002, 1, 1), end_date=date(2003, 12, 31), category="test"
        )
        tp2 = TimePeriod(
            start_date=date(2002, 1, 1), end_date=date(2003, 12, 31), category="ignore"
        )
        wr1.register_time_period(tp1)
        wr1.register_time_period(tp2)

        wr2 = WellRecord(
            api_num="05-123-98765",
            well_name="test well #2",
            first_date=date(2019, 11, 1),
            last_date=date(2023, 5, 1),
        )
        tp3 = TimePeriod(
            start_date=date(2002, 5, 1), end_date=date(2003, 11, 30), category="test"
        )
        wr2.register_time_period(tp3)
        wg = WellGroup()
        wg.add_well_record(wr1)
        wg.add_well_record(wr2)

        gaps = wg.find_gaps(category="test")
        tp_expected = TimePeriod(
            start_date=date(2002, 1, 1), end_date=date(2002, 4, 30), category="test"
        )
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
            tp_expected.start_date,
            f"Expected start date of {tp_expected.start_date}; found {gap.start_date}.",
        )
        # End dates match.
        self.assertEqual(
            gap.end_date,
            tp_expected.end_date,
            f"Expected end date of {tp_expected.end_date}; found {gap.end_date}.",
        )
        # Category is correct.
        self.assertEqual(
            gap.category,
            tp_expected.category,
            f"Expected category {tp_expected.category!r}; found {gap.category!r}",
        )


if __name__ == "__main__":
    unittest.main()
