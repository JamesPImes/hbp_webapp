from __future__ import annotations

from typing import Callable
from datetime import date, datetime, timedelta


def _default_daterange_parse_func(date_str: str) -> DateRange:
    """
    INTERNAL USE:

    Split a date string that follows the default schema
    (``YYYY-MM-DD::YYYY-MM-DD``) into a ``DateRange`` object.
    :param date_str: A string of the form ``'2014-01-01::2015-01-09'``
     that encodes a date range.
    :return:
    """
    try:
        s1, s2 = date_str.split("::")
        date1 = datetime.strptime(s1, "%Y-%m-%d").date()
        date2 = datetime.strptime(s2, "%Y-%m-%d").date()
        return DateRange(date1, date2)
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
        """
        Return the duration in calendar months, including the first and
        last.
        """
        years = self.end_date.year - self.start_date.year
        months = self.end_date.month - self.start_date.month
        return years * 12 + months + 1

    def is_contiguous_with(self, other: DateRange, days_tolerance: int = 1) -> bool:
        """
        Check if another ``DateRange`` is contiguous with this one,
        or if the two overlap.

        :param other: The other ``DateRange`` to check.
        :param days_tolerance: If two ``DateRange`` objects do not
         overlap (strictly speaking) but are within this specified
         number of days, they may be considered as contiguous. Defaults
         to 1 (i.e., if one ``DateRange`` ends on one day and the other
         begins on the next day, they are considered contiguous).
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
        """
        Check whether this ``DateRange`` completely encompasses the
        ``DateRange`` passed as ``other``.
        """
        return (
            self.start_date - timedelta(days=days_tolerance) <= other.start_date
            and self.end_date + timedelta(days=days_tolerance) >= other.end_date
        )

    def merge_with(self, other: DateRange, days_tolerance: int = 1) -> list[DateRange]:
        """
        Merge the ``other`` date range into this one, if they are
        contiguous (within the specified number of ``days_tolerance``).
        If contiguous, will return a list of a single new ``DateRange``.
        If not contiguous, will return a list of two ``DateRange``
        objects (the original date ranges).

        :param other:
        :param days_tolerance:
        :return:
        """
        if not self.is_contiguous_with(other, days_tolerance):
            return [self, other]
        start = min(self.start_date, other.start_date)
        end = max(self.end_date, other.end_date)
        return [DateRange(start, end)]

    def subtract(self, other: DateRange) -> list[DateRange]:
        """
        Carve the ``other`` date range out of this date range, and
        return a list of the resulting ``DateRange`` object(s) -- i.e.,
        between 0 and 2 resulting date ranges.

        :param other:
        :return:
        """
        drs = []
        if not self.is_contiguous_with(other, days_tolerance=0):
            # No overlap, so nothing to cut out.
            drs = [self]

        elif other.encompasses(self, days_tolerance=0):
            # Complete overlap, so deleting this entire date range.
            pass

        elif self.encompasses(other, days_tolerance=0):
            # Middle cut, results in 2 new date ranges.
            dr1 = DateRange(self.start_date, other.start_date - timedelta(days=1))
            drs.append(dr1)
            dr2 = DateRange(other.end_date + timedelta(days=1), self.end_date)
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

    def find_overlap(self, other: DateRange) -> DateRange | None:
        """
        Find the overlap between this date range and the ``other``
        date range. If there is no overlap, return None.

        :param other:
        :return:
        """
        dr = None
        if not self.is_contiguous_with(other, days_tolerance=0):
            pass
        elif other.encompasses(self, days_tolerance=0):
            dr = self
        elif self.encompasses(other, days_tolerance=0):
            dr = other
        # One end or the other is trimmed, but only 1 resulting date range.
        elif other.start_date < self.start_date:
            dr = DateRange(self.start_date, other.end_date)
        else:
            dr = DateRange(other.start_date, self.end_date)
        return dr

    def __str__(self):
        return f"{self.start_date:%Y-%m-%d}::{self.end_date:%Y-%m-%d}"

    def __repr__(self):
        return str(self)


class DateRangeGroup:
    """A collection of ``DateRange`` objects."""

    def __init__(self, date_ranges: list[DateRange] = None) -> None:
        if date_ranges is None:
            date_ranges = []
        self.date_ranges: list[DateRange] = date_ranges

    def add_date_range(self, date_range: DateRange) -> None:
        """Add a ``DateRange`` object, with type checking."""
        if not isinstance(date_range, DateRange):
            raise TypeError("May only add DateRange objects")
        self.date_ranges.append(date_range)

    def sort(self) -> None:
        """Sort the date ranges by start date, then end date."""
        self.date_ranges.sort(key=lambda t: t.start_date)
        self.date_ranges.sort(key=lambda t: t.end_date)

    def merge_all(self, days_tolerance: int = 0) -> None:
        """
        Merge the date ranges into as few as possible, and store the
        results.
        """
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

    def subtract_from_all(self, date_range: DateRange) -> None:
        """
        Subtract the specified date range from every date range stored
        in this group, and store the results. (The ``DateRange`` object
        passed to this method will not be added.)

        :param date_range:
        :return:
        """
        new_drs = []
        for dr in self.date_ranges:
            subtracted = dr.subtract(date_range)
            new_drs.extend(subtracted)
        self.date_ranges = new_drs
        self.sort()

    def find_all_overlaps(self, other: DateRangeGroup) -> DateRangeGroup:
        """
        Find all overlapping date ranges between this ``DateRangeGroup``
        and another ``DateRangeGroup``. Returns a new group.

        :param other:
        :return:
        """
        new_group = DateRangeGroup()
        if len(self.date_ranges) == 0 or len(other.date_ranges) == 0:
            return new_group

        new_drs = []
        for dr_b in other.date_ranges:
            for dr_a in self.date_ranges:
                overlap = dr_a.find_overlap(dr_b)
                if overlap is not None:
                    new_drs.append(overlap)
        new_group.date_ranges = new_drs
        new_group.merge_all()
        return new_group

    def get_date_ranges_of_minimum_duration(self, days: int) -> DateRangeGroup:
        """
        Extract a new ``DateRangeGroup`` whose date ranges are at least
        the specified number of ``days`` in length.
        """
        output_group = DateRangeGroup()
        for dr in self:
            if dr.duration_in_days() >= days:
                output_group.date_ranges.append(dr)
        return output_group

    def get_shortest_and_longest_durations(self) -> (int, int):
        """
        Get the shortest and longest durations (in days) found in this
        group of date ranges, returned as a 2-tuple of ints.
        """
        shortest_duration = 0
        longest_duration = 0
        for dr in self.date_ranges:
            shortest_duration = min(shortest_duration, dr.duration_in_days())
            longest_duration = max(longest_duration, dr.duration_in_days())
        return shortest_duration, longest_duration

    def __str__(self):
        return str(self.date_ranges)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.date_ranges)

    def __getitem__(self, item):
        return self.date_ranges[item]

    def __len__(self):
        return len(self.date_ranges)


__all__ = [
    "DateRange",
    "DateRangeGroup",
]
