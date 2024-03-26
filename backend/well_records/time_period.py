from __future__ import annotations

from typing import Callable
from datetime import date, datetime


def _default_parse_func(date_str: str) -> (date, date):
    """
    :param date_str: "2014-01-01::2015-01-09"
    :return:
    """
    try:
        s1, s2 = date_str.split("::")
        date1 = datetime.strptime(s1, "%Y-%m-%d").date()
        date2 = datetime.strptime(s2, "%Y-%m-%d").date()
        return (date1, date2)
    except ValueError:
        raise ValueError("Date range must be in the format YYYY-MM-DD::YYYY-MM-DD")


class TimePeriod:
    """A period of time."""

    def __init__(
        self, start_date: date, end_date: date, category: str = "default"
    ) -> None:
        if start_date > end_date:
            raise ValueError("Start date must be earlier than end date.")
        self.start_date = start_date
        self.end_date = end_date
        self.category = category

    def duration_in_days(self) -> int:
        """Return the duration in days, including the first and last."""
        return (self.end_date - self.start_date).days + 1

    def duration_in_months(self) -> int:
        """Return the duration in calendar months, including the first and last."""
        years = self.end_date.year - self.start_date.year
        months = self.end_date.month - self.start_date.month
        return years * 12 + months + 1

    @staticmethod
    def from_string(
        date_str: str, parse_func: Callable = None, category: str = None
    ) -> TimePeriod:
        """
        Create a ``TimePeriod`` from a string.

        Default assumes the format ``"YYYY-MM-DD::YYYY-MM-DD"``. If a different format
        is used, ``parse_func`` must also be provided, being a function that will
        split the string into two ``datetime.date`` objects.

        :param date_str: The string to parse into a ``TimePeriod``.
        :param parse_func: The function to split a string into two ``datetime.date``
         objects. (Only required if ``date_str`` is not in the expected format.)
        :param category: (Optional) The category of this ``TimePeriod`` (e.g., "shut-in").
        :return: The new ``TimePeriod`` object.
        """
        if parse_func is None:
            parse_func = _default_parse_func
        date1, date2 = parse_func(date_str)
        return TimePeriod(date1, date2, category)

    def merge_with(self, other: TimePeriod) -> TimePeriod:
        pass

    def subtract_out(self, other: TimePeriod) -> TimePeriod:
        pass

    def __str__(self):
        return f"<{self.start_date:%Y-%m-%d}::{self.end_date:%Y-%m-%d}>"

    def __repr__(self):
        return str(self)


__all__ = [
    "TimePeriod",
]
