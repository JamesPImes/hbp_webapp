from abc import ABC, abstractmethod

from backend.well_records import WellRecord


class WellRecordDataGateway(ABC):
    """Interface for well record data gateway."""

    @abstractmethod
    def insert(self, well_record: WellRecord, **kw) -> None:
        raise NotImplementedError

    @abstractmethod
    def find(self, api_num, **kw) -> WellRecord:
        raise NotImplementedError

    @abstractmethod
    def update(self, well_record, **kw) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, api_num, **kw) -> None:
        raise NotImplementedError


__all__ = [
    "WellRecordDataGateway",
]
