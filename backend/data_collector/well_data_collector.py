from abc import ABC, abstractmethod

from backend.well_record import WellRecord


class WellDataCollector(ABC):
    """Interface for collector of well data."""

    @abstractmethod
    def get_well_data(self, api_num: str, well_name: str, **kw) -> WellRecord:
        raise NotImplementedError


__all__ = [
    "WellDataCollector",
]
