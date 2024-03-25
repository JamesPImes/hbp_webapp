
from datetime import date

from .time_period import TimePeriod


class WellRecord:
    """Production records for a given well."""

    def __init__(
            self,
            api_num: str,
            well_name: str = None,
            effective_date: date = None) -> None:
        self.api_num: str = api_num
        self.well_name: str = well_name
        self.effective_date: date = effective_date
        self.gaps: list[TimePeriod] = []


__all__ = [
    'WellRecord',
]
