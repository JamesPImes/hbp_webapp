from datetime import date

from .time_period import TimePeriod


class WellRecord:
    """Production records for a given well."""

    def __init__(
        self,
        api_num: str,
        well_name: str = None,
        first_date: date = None,
        last_date: date = None,
    ) -> None:
        self.api_num: str = api_num
        self.well_name: str = well_name
        self.first_date: date = first_date
        self.last_date: date = last_date
        self.time_periods: dict[str : list[TimePeriod]] = {}

    def register_time_period(self, time_period: TimePeriod) -> None:
        """
        Register a time period to this well. Will automatically
        be categorized into the ``.time_periods`` dict.
        """
        key = str(time_period.category)
        self.time_periods.setdefault(key, [])
        self.time_periods[key].append(time_period)

    def time_periods_by_cat(self, category) -> list[TimePeriod]:
        """Get a list of time periods that match the specified category."""
        return self.time_periods.get(category, [])

    def __str__(self):
        well_name = self.well_name
        if well_name is None:
            well_name = "No Name"
        return f"WellRecord<{well_name!r} ({self.api_num})>"

    def __repr__(self):
        return str(self)


__all__ = [
    "WellRecord",
]
