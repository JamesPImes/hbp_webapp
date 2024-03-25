from datetime import date

from backend.well_records.well_record import WellRecord
from backend.well_records.time_period import TimePeriod


class WellGroup:
    def __init__(self) -> None:
        self.well_records: list[WellRecord] = []

    def add_well_record(self, well_record: WellRecord) -> None:
        self.well_records.append(well_record)

    def find_first_date(self) -> date:
        pass

    def find_last_date(self) -> date:
        pass

    def find_gaps(self, category) -> list[TimePeriod]:
        pass


__all__ = [
    "WellGroup",
]
