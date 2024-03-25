
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
        self.time_periods: dict[str: list[TimePeriod]] = {}

    def register_time_period(self, time_period: TimePeriod) -> None:
        """
        Register a time period to this well. Will automatically
        be categorized into the ``.time_periods`` dict.
        """
        key = str(time_period.category)
        self.time_periods.setdefault(key, list[TimePeriod])
        self.time_periods[key].append(time_period)


__all__ = [
    'WellRecord',
]
