from __future__ import annotations

from typing import Callable
from datetime import date, datetime, timedelta


def _default_parse_func(date_str: str) -> (date, date):
    """
    :param date_str: "2014-01-01::2015-01-09"
    :return:
    """
    # TODO: Move this to a handler class.
    try:
        s1, s2 = date_str.split("::")
        date1 = datetime.strptime(s1, "%Y-%m-%d").date()
        date2 = datetime.strptime(s2, "%Y-%m-%d").date()
        return (date1, date2)
    except ValueError:
        raise ValueError("Date range must be in the format YYYY-MM-DD::YYYY-MM-DD")


class DateRange:
    """A period of time, represented by start and end dates (inclusive)."""

    def __init__(self, start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise ValueError("Start date must be earlier than end date.")
        self.start_date: date = start_date
        self.end_date: date = end_date

    def duration_in_days(self) -> int:
        """Return the duration in days, including the first and last."""
        return (self.end_date - self.start_date).days + 1

    def duration_in_months(self) -> int:
        """Return the duration in calendar months, including the first and last."""
        years = self.end_date.year - self.start_date.year
        months = self.end_date.month - self.start_date.month
        return years * 12 + months + 1

    @staticmethod
    def from_string(date_str: str, parse_func: Callable = None) -> DateRange:
        """
        Create a ``DateRange`` from a string.

        Default assumes the format ``"YYYY-MM-DD::YYYY-MM-DD"``. If a different format
        is used, ``parse_func`` must also be provided, being a function that will
        split the string into two ``datetime.date`` objects.

        :param date_str: The string to parse into a ``DateRange``.
        :param parse_func: The function to split a string into two ``datetime.date``
         objects. (Only required if ``date_str`` is not in the expected format.)
        :return: The new ``DateRange`` object.
        """
        if parse_func is None:
            parse_func = _default_parse_func
        date1, date2 = parse_func(date_str)
        return DateRange(date1, date2)

    def is_contiguous_with(self, other: DateRange, days_tolerance: int = 1) -> bool:
        """
        Check if another ``DateRange`` is contiguous with this one,
        or if the two overlap.

        :param other: The other ``DateRange`` to check.
        :param days_tolerance: If two ``DateRange`` objects do
         not overlap (strictly speaking) but are within this
         specified number of days, they may be considered as
         contiguous. Defaults to 1 (i.e., if one ``DateRange`` ends
         on one day and the other begins on the next day, they are
         considered contiguous).
        """
        if (
            self.start_date - timedelta(days=days_tolerance)
            <= other.end_date
            <= self.end_date + timedelta(days=days_tolerance)
        ):
            return True
        elif (
            other.start_date - timedelta(days=days_tolerance)
            <= self.end_date
            <= other.end_date + timedelta(days=days_tolerance)
        ):
            return True
        return False

    def encompasses(self, other: DateRange, days_tolerance: int = 1) -> bool:
        return (
            self.start_date - timedelta(days=days_tolerance) < other.start_date
            and self.end_date + timedelta(days=days_tolerance) > other.end_date
        )

    def merge_with(self, other: DateRange, days_tolerance: int = 1) -> list[DateRange]:
        if not self.is_contiguous_with(other, days_tolerance):
            return [self, other]
        start = min(self.start_date, other.start_date)
        end = max(self.end_date, other.end_date)
        return [DateRange(start, end)]

    def subtract(self, other: DateRange) -> list[DateRange]:
        drs = []
        if not self.is_contiguous_with(other, days_tolerance=0):
            # No overlap, so nothing to cut out.
            drs = [self]

        elif other.encompasses(self, days_tolerance=0):
            # Complete overlap, so deleting this entire date range.
            pass

        elif self.encompasses(other, days_tolerance=0):
            # Middle cut, results in 2 new date ranges.
            start1 = self.start_date
            end1 = other.start_date - timedelta(days=1)
            dr1 = DateRange(start1, end1)
            drs.append(dr1)
            start2 = other.end_date + timedelta(days=1)
            end2 = self.end_date
            dr2 = DateRange(start2, end2)
            drs.append(dr2)

        # One end or the other is trimmed, but only 1 resulting date range.
        elif other.start_date < self.start_date:
            # Trimming the front end.
            dr = DateRange(other.end_date + timedelta(days=1), self.end_date)
            drs.append(dr)
        else:
            # Trimming the back end.
            dr = DateRange(self.start_date, other.start_date - timedelta(days=1))
            drs.append(dr)
        return drs

    def __str__(self):
        return f"<{self.start_date:%Y-%m-%d}::{self.end_date:%Y-%m-%d}>"

    def __repr__(self):
        return str(self)


class DateRangeGroup:
    def __init__(self, date_ranges: list[DateRange] = None) -> None:
        if date_ranges is None:
            date_ranges = []
        self.date_ranges: list[DateRange] = date_ranges

    def add_date_range(self, date_range: DateRange) -> None:
        if not isinstance(DateRange):
            raise TypeError("May only add DateRange objects")
        self.date_ranges.append(date_range)

    def sort(self) -> None:
        self.date_ranges.sort(key=lambda t: t.start_date)
        self.date_ranges.sort(key=lambda t: t.end_date)

    def merge_all(self, days_tolerance: int = 0) -> None:
        self.sort()
        drs = self.date_ranges
        new_drs = []
        while len(drs) != len(new_drs):
            new_drs = []
            for i in range(0, len(drs), 2):
                j = min(i + 1, len(drs) - 1)
                merged = drs[i].merge_with(drs[j], days_tolerance)
                new_drs.extend(merged)
            drs = new_drs
        self.date_ranges = new_drs

    def subtract_from_all(self, time_period: DateRange) -> None:
        new_drs = []
        for dr in self.date_ranges:
            subtracted = dr.subtract(time_period)
            new_drs.extend(subtracted)
        self.date_ranges = new_drs
        self.sort()


__all__ = [
    "DateRange",
    "DateRangeGroup",
]
