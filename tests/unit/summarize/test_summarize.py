import unittest
from datetime import date

from backend.well_record import DateRange, DateRangeGroup, WellRecord
from backend.data_analyzer import WellGroup
from backend.summarize import (
    summarize_date_range,
    summarize_date_range_group,
    summarize_well_record,
    summarize_well_group,
)


class TestSummarizeDateRange(unittest.TestCase):

    dr: DateRange = None

    @classmethod
    def setUpClass(cls):
        cls.dr = DateRange(date(2020, 1, 1), date(2020, 12, 31))

    def test_summarize_date_range_without_daysmonths(self):
        summary = summarize_date_range(
            self.dr, between_dates="_", show_days=False, show_months=False
        )
        expected = "2020-01-01_2020-12-31"
        self.assertEqual(expected, summary)

    def test_summarize_date_range_with_daysmonths(self):
        summary = summarize_date_range(
            self.dr, between_dates="_", show_days=True, show_months=True
        )
        expected = "2020-01-01_2020-12-31 (366 days; 12 calendar months)"
        self.assertEqual(expected, summary)


class TestSummarizeDateRangeGroup(unittest.TestCase):

    dr0: DateRange = None
    dr1: DateRange = None
    drg: DateRangeGroup = None

    @classmethod
    def setUpClass(cls):
        cls.dr0 = DateRange(date(2020, 1, 1), date(2020, 12, 31))
        cls.dr1 = DateRange(date(2022, 1, 1), date(2022, 6, 30))
        cls.drg = DateRangeGroup([cls.dr0, cls.dr1])

    def test_summarize_drg_without_daysmonths(self):
        summary = summarize_date_range_group(
            self.drg, between_dates="_", show_days=False, show_months=False
        )
        dr0_expected = "2020-01-01_2020-12-31"
        dr1_expected = "2022-01-01_2022-06-30"
        expected_longest_days = 366
        self.assertEqual(dr0_expected, summary["Date Ranges"][0])
        self.assertEqual(dr1_expected, summary["Date Ranges"][1])
        self.assertEqual(expected_longest_days, summary["Longest (days)"])

    def test_summarize_drg_with_daysmonths(self):
        summary = summarize_date_range_group(
            self.drg, between_dates="_", show_days=True, show_months=True
        )
        dr0_expected = "2020-01-01_2020-12-31 (366 days; 12 calendar months)"
        dr1_expected = "2022-01-01_2022-06-30 (181 days; 6 calendar months)"
        expected_longest_days = 366
        self.assertEqual(dr0_expected, summary["Date Ranges"][0])
        self.assertEqual(dr1_expected, summary["Date Ranges"][1])
        self.assertEqual(expected_longest_days, summary["Longest (days)"])


class TestSummarizeWellRecord(unittest.TestCase):

    dr0: DateRange = None
    dr1: DateRange = None
    drg: DateRangeGroup = None
    wr: WellRecord = None
    category_descriptions: dict = None
    expected_fields: dict = None

    @classmethod
    def setUpClass(cls):
        cls.dr0 = DateRange(date(2020, 1, 1), date(2020, 12, 31))
        cls.dr1 = DateRange(date(2022, 1, 1), date(2022, 6, 30))
        cls.drg = DateRangeGroup([cls.dr0, cls.dr1])
        cls.wr = WellRecord(
            api_num="05-123-45678",
            well_name="Test Well #1",
            first_date=date(2010, 1, 1),
            last_date=date(2024, 1, 1),
            record_access_date=date(2024, 4, 12),
        )
        cls.wr.register_empty_category("Test Category")
        for dr in (cls.dr0, cls.dr1):
            cls.wr.register_date_range(dr, "Test Category")
        cls.category_descriptions = {"Test Category": "Test Category Description"}
        cls.expected_fields = {
            "API Number": "05-123-45678",
            "Well Name": "Test Well #1",
            "First Date of Production": "2010-01-01",
            "Last Date of Production": "2024-01-01",
            "Record Access Date": "2024-04-12",
        }

    def test_summarize_well_record_without_daysmonths(self):
        summary = summarize_well_record(
            self.wr,
            category_descriptions=self.category_descriptions,
            between_dates="_",
            show_days=False,
            show_months=False,
        )
        for field, data in self.expected_fields.items():
            self.assertEqual(data, summary[field])

        self.assertEqual(1, len(summary["Date Ranges"]))
        for category, description in self.category_descriptions.items():
            drg_summary = summary["Date Ranges"][category]
            self.assertEqual(description, drg_summary["Description"])
            dr0_expected = "2020-01-01_2020-12-31"
            dr1_expected = "2022-01-01_2022-06-30"
            expected_longest_days = 366
            self.assertEqual(dr0_expected, drg_summary["Date Ranges"][0])
            self.assertEqual(dr1_expected, drg_summary["Date Ranges"][1])
            self.assertEqual(expected_longest_days, drg_summary["Longest (days)"])

    def test_summarize_well_record_with_daysmonths(self):
        summary = summarize_well_record(
            self.wr,
            category_descriptions=self.category_descriptions,
            between_dates="_",
            show_days=True,
            show_months=True,
        )
        for field, data in self.expected_fields.items():
            self.assertEqual(data, summary[field])

        self.assertEqual(1, len(summary["Date Ranges"]))
        for category, description in self.category_descriptions.items():
            drg_summary = summary["Date Ranges"][category]
            self.assertEqual(description, drg_summary["Description"])
            dr0_expected = "2020-01-01_2020-12-31 (366 days; 12 calendar months)"
            dr1_expected = "2022-01-01_2022-06-30 (181 days; 6 calendar months)"
            expected_longest_days = 366
            self.assertEqual(dr0_expected, drg_summary["Date Ranges"][0])
            self.assertEqual(dr1_expected, drg_summary["Date Ranges"][1])
            self.assertEqual(expected_longest_days, drg_summary["Longest (days)"])


class TestSummarizeWellGroup(unittest.TestCase):

    dr0: DateRange = None
    dr1: DateRange = None
    dr2: DateRange = None
    wr0: WellRecord = None
    wr1: WellRecord = None
    wg: WellGroup = None
    category_descriptions: dict = None
    expected_fields: dict = None

    @classmethod
    def setUpClass(cls):
        cls.dr0 = DateRange(date(2020, 1, 1), date(2020, 12, 31))
        cls.dr1 = DateRange(date(2022, 1, 1), date(2022, 6, 30))
        cls.wr0 = WellRecord(
            api_num="05-123-45678",
            well_name="Test Well #1",
            first_date=date(2010, 1, 1),
            last_date=date(2024, 1, 1),
            record_access_date=date(2024, 4, 12),
        )
        cls.wr0.register_empty_category("Test Category")
        for dr in (cls.dr0, cls.dr1):
            cls.wr0.register_date_range(dr, "Test Category")

        cls.dr2 = DateRange(date(2020, 1, 1), date(2020, 6, 30))
        cls.wr1 = WellRecord(
            api_num="05-456-98765",
            well_name="Test Well #2",
            first_date=date(1999, 1, 1),
            last_date=date(2023, 1, 1),
            record_access_date=date(2024, 4, 10),
        )
        cls.wr1.register_empty_category("Test Category")
        cls.wr1.register_date_range(cls.dr2, "Test Category")

        cls.wg = WellGroup()
        for wr in (cls.wr0, cls.wr1):
            cls.wg.add_well_record(wr)
        # Should be a single gap, from 2020-01-01 through 2020-06-30.
        cls.wg.find_gaps("Test Category")

        cls.category_descriptions = {"Test Category": "Test Category Description"}
        cls.expected_fields = {
            "Well Count": 2,
            "API Numbers": ["05-123-45678", "05-456-98765"],
            "Earliest Reported Date": "1999-01-01",
            "Latest Reported Date": "2024-01-01",
        }

    def test_summarize_well_record_without_daysmonths(self):
        summary = summarize_well_group(
            self.wg,
            category_descriptions=self.category_descriptions,
            between_dates="_",
            show_days=False,
            show_months=False,
        )
        for field, data in self.expected_fields.items():
            self.assertEqual(data, summary[field])
        self.assertEqual(2, len(summary["Well Records"]))

        gaps_summary = summary["Researched Gaps"]
        print(gaps_summary)
        self.assertEqual(1, len(gaps_summary))
        for category, description in self.category_descriptions.items():
            drg_summary = gaps_summary[category]
            self.assertEqual(description, drg_summary["Description"])
            # Only 1 gap found.
            self.assertEqual(1, len(drg_summary["Date Ranges"]))
            gap_expected = "2020-01-01_2020-06-30"
            expected_longest_days = 182
            self.assertEqual(gap_expected, drg_summary["Date Ranges"][0])
            self.assertEqual(expected_longest_days, drg_summary["Longest (days)"])

    def test_summarize_well_record_with_daysmonths(self):
        summary = summarize_well_group(
            self.wg,
            category_descriptions=self.category_descriptions,
            between_dates="_",
            show_days=True,
            show_months=True,
        )
        for field, data in self.expected_fields.items():
            self.assertEqual(data, summary[field])
        self.assertEqual(2, len(summary["Well Records"]))

        gaps_summary = summary["Researched Gaps"]
        print(gaps_summary)
        self.assertEqual(1, len(gaps_summary))
        for category, description in self.category_descriptions.items():
            drg_summary = gaps_summary[category]
            self.assertEqual(description, drg_summary["Description"])
            # Only 1 gap found.
            self.assertEqual(1, len(drg_summary["Date Ranges"]))
            gap_expected = "2020-01-01_2020-06-30 (182 days; 6 calendar months)"
            expected_longest_days = 182
            self.assertEqual(gap_expected, drg_summary["Date Ranges"][0])
            self.assertEqual(expected_longest_days, drg_summary["Longest (days)"])


if __name__ == "__main__":
    unittest.main()
