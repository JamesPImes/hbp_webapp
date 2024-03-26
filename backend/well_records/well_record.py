from datetime import date

from .date_range import DateRange


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
        self.date_ranges: dict[str: list[DateRange]] = {}

    def register_date_range(self, date_range: DateRange) -> None:
        """
        Register a time period to this well. Will automatically
        be categorized into the ``.date_ranges`` dict.
        """
        key = str(date_range.category)
        self.date_ranges.setdefault(key, [])
        self.date_ranges[key].append(date_range)

    def date_ranges_by_category(self, category) -> list[DateRange]:
        """Get a list of time periods that match the specified category."""
        return self.date_ranges.get(category, [])

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
