from __future__ import annotations

from typing import Callable
from datetime import date, datetime, timedelta


DEFAULT_CATEGORY = "default"


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
        self, start_date: date, end_date: date, category: str = DEFAULT_CATEGORY
    ) -> None:
        if start_date > end_date:
            raise ValueError("Start date must be earlier than end date.")
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.category: str = category

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

    def is_contiguous_with(self, other: TimePeriod, days_tolerance: int = 1) -> bool:
        """
        Check if another ``TimePeriod`` is contiguous with this one,
        or if the two overlap.

        :param other: The other ``TimePeriod`` to check.
        :param days_tolerance: If two ``TimePeriod`` objects do
         not overlap (strictly speaking) but are within this
         specified number of days, they may be considered as
         contiguous. Defaults to 1 (i.e., if one ``TimePeriod`` ends
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

    def encompasses(self, other: TimePeriod, days_tolerance: int = 1) -> bool:
        return (
            self.start_date - timedelta(days=days_tolerance) < other.start_date
            and self.end_date + timedelta(days=days_tolerance) > other.end_date
        )

    def merge_with(
        self, other: TimePeriod, days_tolerance: int = 1
    ) -> list[TimePeriod]:
        if not self.is_contiguous_with(other, days_tolerance):
            return [self, other]
        start = min(self.start_date, other.start_date)
        end = max(self.end_date, other.end_date)
        return [TimePeriod(start, end, category=self.category)]

    def subtract(self, other: TimePeriod) -> list[TimePeriod]:
        tps = []
        if not self.is_contiguous_with(other, days_tolerance=0):
            # No overlap, so nothing to cut out.
            tps = [self]

        elif other.encompasses(self, days_tolerance=0):
            # Complete overalp, so deleting this entire time period.
            pass

        elif self.encompasses(other, days_tolerance=0):
            # Middle cut, results in 2 new time periods.
            start1 = self.start_date
            end1 = other.start_date - timedelta(days=1)
            tp1 = TimePeriod(start1, end1, category=self.category)
            tps.append(tp1)
            start2 = other.end_date + timedelta(days=1)
            end2 = self.end_date
            tp2 = TimePeriod(start2, end2, category=self.category)
            tps.append(tp2)

        # One end or the other is trimmed, but only 1 resulting time period.
        elif other.start_date < self.start_date:
            # Trimming the front end.
            tp = TimePeriod(
                other.end_date + timedelta(days=1),
                self.end_date,
                category=self.category,
            )
            tps.append(tp)
        else:
            # Trimming the back end.
            tp = TimePeriod(
                self.start_date,
                other.start_date - timedelta(days=1),
                category=self.category,
            )
            tps.append(tp)
        return tps

    def __str__(self):
        return f"<{self.start_date:%Y-%m-%d}::{self.end_date:%Y-%m-%d}>"

    def __repr__(self):
        return str(self)


class TimePeriodGroup:
    def __init__(
        self, time_periods: list[TimePeriod] = None, category: str = DEFAULT_CATEGORY
    ) -> None:
        self.category = category
        if time_periods is None:
            time_periods = []
        self.time_periods: list[TimePeriod] = time_periods

    def sort(self) -> None:
        self.time_periods.sort(key=lambda t: t.start_date)
        self.time_periods.sort(key=lambda t: t.end_date)

    def merge_all(self, days_tolerance: int = 0) -> None:
        self.sort()
        tps = self.time_periods
        new_tps = []
        while len(tps) != len(new_tps):
            new_tps = []
            for i in range(0, len(tps), 2):
                j = min(i + 1, len(tps) - 1)
                merged = tps[i].merge_with(tps[j], days_tolerance)
                new_tps.extend(merged)
            tps = new_tps
        self.time_periods = new_tps


__all__ = [
    "TimePeriod",
    "TimePeriodGroup",
]
