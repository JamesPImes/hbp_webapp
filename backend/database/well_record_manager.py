from abc import ABC

from backend.well_records.well_record import WellRecord


class WellRecordManager(ABC):
    """Interface for well record manager."""
    def insert_well_record(self, well_record: WellRecord, **kw) -> None:
        raise NotImplementedError

    def find_well_record(self, api_num, **kw) -> WellRecord:
        raise NotImplementedError

    def update_well_record(self, well_record, **kw) -> None:
        raise NotImplementedError

    def delete_well_record(self, api_num, **kw) -> None:
        raise NotImplementedError


__all__ = [
    "WellRecordManager",
]
