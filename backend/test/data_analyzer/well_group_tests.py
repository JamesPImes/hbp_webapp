import unittest

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
        pass

    def test_find_last_date(self):
        pass

    def test_find_gaps(self):
        pass


if __name__ == "__main__":
    unittest.main()
