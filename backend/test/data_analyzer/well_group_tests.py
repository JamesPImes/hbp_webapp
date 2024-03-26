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
        pass

    def test_find_gaps(self):
        pass


if __name__ == "__main__":
    unittest.main()
