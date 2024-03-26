from datetime import date

from backend.well_records.well_record import WellRecord
from backend.well_records.date_range import DateRange


class WellGroup:
    def __init__(self) -> None:
        self.well_records: list[WellRecord] = []

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

    def find_inverse_time_periods(self, category):
        overall_first_date = self.find_first_date()
        overall_last_date = self.find_last_date()
        all_tps = []
        for wr in self.well_records:
            sub_first = wr.first_date
            sub_lsat = wr.last_date
            tps = wr.date_ranges_by_category(category)


    def find_gaps(self, category) -> list[DateRange]:
        pass


__all__ = [
    "WellGroup",
]
