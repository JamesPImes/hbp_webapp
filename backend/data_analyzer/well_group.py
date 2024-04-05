from datetime import date, timedelta

from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange, DateRangeGroup


class WellGroup:
    def __init__(self) -> None:
        self.well_records: list[WellRecord] = []
        self.researched_gaps: dict[str, DateRangeGroup] = {}

    def add_well_record(self, well_record: WellRecord) -> None:
        """Add a well record to this well group."""
        self.well_records.append(well_record)

    def find_first_date(self) -> date:
        """
        Find the earliest date in any of the well records.
        Returns None if no added records have a first date specified.
        """
        first = None
        for wr in self.well_records:
            if first is None:
                first = wr.first_date
            elif wr.first_date is not None and wr.first_date < first:
                first = wr.first_date
        return first

    def find_last_date(self) -> date:
        """
        Find the latest date in any of the well records.
        Returns None if no added records have a last date specified.
        """
        last = None
        for wr in self.well_records:
            if last is None:
                last = wr.last_date
            elif wr.last_date is not None and wr.last_date > last:
                last = wr.last_date
        return last

    def shared_categories(self) -> list[str]:
        """
        Get a list of category names that are shared by all well records
        in this group.
        :return:
        """
        categories = set()
        if len(self.well_records) == 0:
            return []
        for i, wr in enumerate(self.well_records):
            if i == 0:
                categories = set(self.well_records[0].registered_categories())
                continue
            categories.intersection_update(wr.registered_categories())
        return sorted(categories)

    def find_gaps(self, category: str) -> DateRangeGroup:
        """
        Find gaps of the specified ``category`` across all well records.
        This takes a "swiss cheese" approach -- i.e., if one well has a
        gap from 1/1/2001 to 1/1/2002 and the only other well only has a
        gap between 7/1/2001 and 7/1/2002, the only remaining gap will
        be identified as 7/1/2001 - 1/1/2002.

        .. note::
           Ensure that the specified ``category`` has been registered
           for each well. Otherwise, this method will raise a
           ``KeyError``. (This ensures that missing data for one well
           does not result in the assumption that no gaps exist for that
           well.)

        :param category: The category of date ranges to find gaps for.
        :return:
        """
        overall_first_date = self.find_first_date()
        overall_last_date = self.find_last_date()

        for wr in self.well_records:
            if category not in wr.registered_categories():
                raise KeyError(f"Must registered category {category!r} for well {wr}")

        gaps_meaningfully_initialized = False
        gaps = DateRangeGroup()
        for i, wr in enumerate(self.well_records):
            original_dr_group = wr.date_ranges_by_category(category)
            # Normalize each WellRecord's gaps to the overall first and last
            # dates (i.e., add gaps before earliest records, and after last
            # records, if necessary.)
            normalized_dr_group = DateRangeGroup(original_dr_group.date_ranges)
            if None in (wr.first_date, wr.last_date) and wr.first_date != wr.last_date:
                raise ValueError(
                    f"First and last date must both be None, or neither may be None. Fix records for {wr}"
                )
            if None in (wr.first_date, wr.last_date):
                continue

            if overall_first_date < wr.first_date:
                normalized_dr_group.add_date_range(
                    DateRange(overall_first_date, wr.first_date - timedelta(days=1))
                )
            if overall_last_date > wr.last_date:
                normalized_dr_group.add_date_range(
                    DateRange(wr.last_date + timedelta(days=1), overall_last_date)
                )

            if i == 0 or not gaps_meaningfully_initialized:
                # Populate the initial gaps with the first well's date ranges.
                gaps = normalized_dr_group
                gaps_meaningfully_initialized = True
                continue
            if len(gaps.date_ranges) == 0:
                # Once we've removed all date ranges, there can never be future gaps.
                break
            gaps = gaps.find_all_overlaps(normalized_dr_group)
        self.researched_gaps[category] = gaps
        return gaps

    def summarize(
        self,
        category_clean_names: dict[str, str] = None,
        between="::",
        show_days: bool = False,
        show_months: bool = False,
    ) -> dict:
        """
        Summarize this well group's data fields into a dict.

        :param category_clean_names: (Optional) Pass a dict whose keys
         are the 'official' categories of date ranges registered to the
         well records; and whose values are the 'clean' version that
         should appear in the output dict instead (e.g.,
         ``{'NO_PROD_IGNORE_SHUTIN'``: ``'No production (ignore shutin)'}``.
        :param between: The string to go between the start/end date of
         each date range. (Default: ``'::'``).
        :param show_days: Whether to include the duration of each date
         range in days. (Default: ``False``)
        :param show_months: Whether to include the duration of each date
         range in calendar months. (Default: ``False``)
        """
        if category_clean_names is None:
            category_clean_names = {}
        summary = {
            "Well Count": len(self.well_records),
            "API Numbers": [wr.api_num for wr in self.well_records],
            "Earliest Reported Date": self.find_first_date(),
            "Latest Reported Date": self.find_last_date(),
            "Researched Gaps": {},
            "Researched Gaps<MAX DAYS>": {},
            "Well Records": [],
        }
        for category, gaps in self.researched_gaps.items():
            cat_name = category_clean_names.get(category, category)
            gaps_summary = gaps.summarize_date_ranges(
                between=between,
                show_days=show_days,
                show_months=show_months,
            )
            _, longest_gap = gaps.get_shortest_and_longest_durations()
            summary["Researched Gaps"][cat_name] = gaps_summary
            summary["Researched Gaps<MAX DAYS>"][cat_name] = longest_gap
        for wr in self.well_records:
            wrsummary = wr.summary_dict(
                category_clean_names=category_clean_names,
                between=between,
                show_days=show_days,
                show_months=show_months,
            )
            summary["Well Records"].append(wrsummary)
        return summary


__all__ = [
    "WellGroup",
]
