from __future__ import annotations
from datetime import date, datetime
from typing import Callable

from .date_range import DateRange, DateRangeGroup, _default_daterange_parse_func


def _convert_date(d: datetime | None) -> date | None:
    """
    INTERNAL USE:

    Convert a ``datetime`` to a ``date`` object. If ``d`` is None,
    return None.
    :param d:
    :return:
    """
    if isinstance(d, datetime):
        return d.date()
    elif isinstance(d, date) or d is None:
        return d
    raise TypeError("Passed object is neither `None` nor of type `datetime` or `date`.")


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

    @staticmethod
    def from_dict(
        d: dict, unpack_date_ranges_func: Callable = _default_daterange_parse_func
    ) -> WellRecord:
        """
        Convert a dict ``d`` into a ``WellRecord``. The dict should
        contain the following keys and values (with types):

        - ``'api_num'`` (str): The unique API number for this well.
            (Technically, this is the only required key in the dict.)

        - ``'well_name'`` (str): The name of the well.

        - ``'first_date'`` (``datetime``, ``date``, or ``None``): The
            first date of production records.

        - ``'last_date'`` (``datetime``, ``date``, or ``None``): The
            last date of production records.

        - ``'record_access_date'`` (``datetime``, ``date``, or
            ``None``): The date on which the production records were
            pulled from the official source.

        - ``'date_ranges'`` (``dict[str: list[str]]``): A dict of lists,
            keyed by the name of the category of the date range, with
            each list containing the respective date ranges, each in the
            form of a string (e.g., ``'2019-01-01::2020-12-31'``, the
            default format).

        Any other keys will be ignored.

        :param d: The dict to convert to a ``WellRecord`` (with keys and
         values as stated above).
        :param unpack_date_ranges_func: This function will take in each
         date range string in the lists stored at ``d['date_ranges']``
         and convert them to a ``DateRange`` object. The default
         function assumes that the date range strings are formatted as
         ``'2019-01-01::2020-12-31'``.
        :return: A new ``WellRecord`` with all date ranges registered.
        """
        wr = WellRecord(
            api_num=d.get("api_num"),
            well_name=d.get("well_name"),
            first_date=_convert_date(d.get("first_date")),
            last_date=_convert_date(d.get("last_date")),
            record_access_date=_convert_date(d.get("record_access_date")),
        )
        for category, date_ranges_raw in d.get("date_ranges", {}).items():
            wr.register_empty_category(category)
            for dr_raw in date_ranges_raw:
                dr = unpack_date_ranges_func(dr_raw)
                wr.register_date_range(dr, category)
        return wr

    def summary_dict(
        self,
        category_clean_names: dict[str, str] = None,
        between="::",
        show_days: bool = False,
        show_months: bool = False,
    ) -> dict:
        """
        Summarize this well record's data fields into a dict.
        :param category_clean_names: (Optional) Pass a dict whose keys
         are the 'official' categories of date ranges registered to this
         well record; and whose values are the 'clean' version that
         should appear in the output dict instead (e.g.,
         ``{'NO_PROD_IGNORE_SHUTIN'``: ``'No production (ignore shutin)'}``.
        :param between: The string to go between the start/end date of
         each date range. (Default: ``'::'``).
        :param show_days: Whether to include the duration of each date
         range in days. (Default: ``False``)
        :param show_months: Whether to include the duration of each date
         range in calendar months. (Default: ``False``)
        :return: A dict summarizing the fields in this well record.
        """
        if category_clean_names is None:
            category_clean_names = {}
        data_fields = {
            "API Number": self.api_num,
            "Well Name": "Unknown",
            "First Date of Production": "No production reported",
            "Last Date of Production": "No production reported",
            "Records Access Date": "Unknown",
            "Date Ranges": {},
            "Date Ranges<MAX DAYS>": {},
        }
        if self.well_name is not None:
            data_fields["Well Name"] = self.well_name
        if self.first_date is not None:
            data_fields["First Date of Production"] = f"{self.first_date:%m/%d/%Y}"
        if self.last_date is not None:
            data_fields["Last Date of Production"] = f"{self.last_date:%m/%d/%Y}"
        if self.record_access_date is not None:
            data_fields["Records Access Date"] = f"{self.record_access_date:%m/%d/%Y}"
        for category in self.registered_categories():
            drgroup = self.date_ranges_by_category(category)
            _, longest_duration = drgroup.get_shortest_and_longest_durations()
            drgroup_summary = drgroup.summarize_date_ranges(
                between=between, show_days=show_days, show_months=show_months
            )
            cat_name = category_clean_names.get(category, category)
            data_fields["Date Ranges"][cat_name] = drgroup_summary
            data_fields[f"Date Ranges<MAX DAYS>"][cat_name] = longest_duration
        return data_fields

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
