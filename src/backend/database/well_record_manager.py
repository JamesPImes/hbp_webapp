from abc import ABC

from backend.well_records.well_record import WellRecord


class WellRecordManager(ABC):
    """Interface for well record manager."""
    def insert_well_record(self, well_record: WellRecord) -> None:
        raise NotImplementedError

    def find_well_record(self, **kw) -> WellRecord:
        raise NotImplementedError

    def update_well_record(self, well_record) -> None:
        raise NotImplementedError

    def delete_well_record(self, **kw) -> None:
        raise NotImplementedError


__all__ = [
    "WellRecordManager",
]
