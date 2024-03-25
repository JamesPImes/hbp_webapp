
from __future__ import annotations

from typing import Callable
from datetime import date, datetime


def _default_parse_func(date_str: str) -> (date, date):
    """
    :param date_str: "2014-01-01::2015-01-09"
    :return:
    """
    try:
        s1, s2 = date_str.split('::')
        date1 = datetime.strptime(s1, '%Y-%m-%d').date()
        date2 = datetime.strptime(s2, '%Y-%m-%d').date()
        assert date1 >= date2, "Dates must be in order."
        return (date1, date2)
    except ValueError:
        raise ValueError("Date range must be in the format YYYY-MM-DD::YYYY-MM-DD")


class TimePeriod:
    """A period of time."""

    def __init__(self, start_date: date, end_date: date, category: str = None) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.category = category

    def duration_in_days(self) -> int:
        """Return the duration in days."""
        return (self.end_date - self.start_date).days

    @staticmethod
    def from_string(date_str: str, parse_func: Callable = None, category: str = None) -> TimePeriod:
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


__all__ = [
    'TimePeriod',
]
