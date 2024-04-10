from abc import ABC

from backend.well_records import WellRecord


class WellRecordDataGateway(ABC):
    """Interface for well record data gateway."""
    def insert(self, well_record: WellRecord, **kw) -> None:
        raise NotImplementedError

    def find(self, api_num, **kw) -> WellRecord:
        raise NotImplementedError

    def update(self, well_record, **kw) -> None:
        raise NotImplementedError

    def delete(self, api_num, **kw) -> None:
        raise NotImplementedError


__all__ = [
    "WellRecordDataGateway",
]
