from __future__ import annotations
from datetime import date

from .date_range import DateRange, DateRangeGroup


class WellRecord:
    """Production records for a given well."""

    def __init__(
        self,
        api_num: str,
        well_name: str = None,
        first_date: date = None,
        last_date: date = None,
        record_access_date: date = None,
    ) -> None:
        self.api_num: str = api_num
        self.well_name: str = well_name
        self.first_date: date = first_date
        self.last_date: date = last_date
        self.record_access_date: date = record_access_date
        self.date_ranges: dict[str:DateRangeGroup] = {}

    def register_date_range(self, date_range: DateRange, category: str) -> None:
        """
        Register a date range to this well to the specified
        ``category``.
        """
        self.date_ranges.setdefault(category, DateRangeGroup())
        self.date_ranges[category].add_date_range(date_range)
        return None

    def register_empty_category(self, category: str) -> None:
        """
        Register the specified ``category`` without adding any date
        ranges to it. If the category already exists, this will have no
        effect.

        :param category:
        :return:
        """
        self.date_ranges.setdefault(category, DateRangeGroup())
        return None

    def registered_categories(self) -> list[str]:
        """
        Get a list of categories that have been registered for this
        well.
        """
        return list(self.date_ranges.keys())

    def date_ranges_by_category(self, category) -> DateRangeGroup:
        """Get the ``DateRangeGroup`` for the specified ``category``."""
        return self.date_ranges.get(category, DateRangeGroup())

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
