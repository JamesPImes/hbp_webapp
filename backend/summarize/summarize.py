"""
Functions to summarize various objects into dicts that can be jsonified.
"""

from backend.data_analyzer import WellGroup
from backend.well_record import WellRecord, DateRange, DateRangeGroup


def summarize_date_range(
    dr: DateRange, between="::", show_days: bool = False, show_months: bool = False
) -> str:
    """
    Summarize a date range as a string.

    :param dr: The ``DateRange`` instance to summarize.
    :param between: The string to go between the start/end date of each
     date range. (Default: ``'::'``).
    :param show_days: Whether to include the duration of each date range
     in days. (Default: ``False``)
    :param show_months: Whether to include the duration of each date
     range in calendar months. (Default: ``False``)
    :return:
    """
    summary = f"{dr.start_date:%Y-%m-%d}{between}{dr.end_date:%Y-%m-%d}"
    additional_info = []
    if show_days:
        additional_info.append(f"{dr.duration_in_days()} days")
    if show_months:
        additional_info.append(f"{dr.duration_in_months()} calendar months")
    if additional_info:
        summary += f" ({'; '.join(additional_info)})"
    return summary


def summarize_date_range_group(
    drg: DateRangeGroup,
    between="::",
    show_days: bool = False,
    show_months: bool = False,
) -> dict:
    """
    Summarize a group of date ranges into a dict with keys
    ``'Longest (days)'`` (the longest duration found in any date range)
    and ``'Date Ranges'`` (a list of summary strings, each representing
    a date range, the format of which is configured with the parameters
    of this function).

    The parameters here (other than ``drg``) are the same as those in
    the ``summarize_date_range()`` function.

    :param drg: The ``DateRangeGroup`` instance to summarize.
    :param between: The string to go between the start/end date of each
     date range. (Default: ``'::'``).
    :param show_days: Whether to include the duration of each date range
     in days. (Default: ``False``)
    :param show_months: Whether to include the duration of each date
     range in calendar months. (Default: ``False``)
    :return: A summary dict as described above.
    """
    _, longest = drg.get_shortest_and_longest_durations()
    summary = {
        "Longest (days)": longest,
        "Date Ranges": [
            summarize_date_range(dr, between, show_days, show_months)
            for dr in drg.date_ranges
        ],
    }
    return summary


def summarize_well_record(
    wr: WellRecord,
    category_descriptions: dict[str, str] = None,
    between="::",
    show_days: bool = False,
    show_months: bool = False,
) -> dict:
    """
    Summarize a well record's data fields into a dict.

    :param wr: The ``WellRecord`` instance to summarize.
    :param category_descriptions: (Optional) Pass a dict whose keys are
     the 'official' categories of date ranges registered to the well
     record; and whose values are a brief description of what that
     category means (e.g.,
     ``{'NO_PROD_IGNORE_SHUTIN'``: ``'No production (ignore shut-in)'}``).
    :param between: The string to go between the start/end date of each
     date range. (Default: ``'::'``).
    :param show_days: Whether to include the duration of each date range
     in days. (Default: ``False``)
    :param show_months: Whether to include the duration of each date
     range in calendar months. (Default: ``False``)
    :return: A dict summarizing the fields in the well record.
    """
    if category_descriptions is None:
        category_descriptions = {}
    data_fields = {
        "API Number": wr.api_num,
        "Well Name": "Unknown",
        "First Date of Production": "No production reported",
        "Last Date of Production": "No production reported",
        "Record Access Date": "Unknown",
        "Date Ranges": {},
    }
    if wr.well_name is not None:
        data_fields["Well Name"] = wr.well_name
    if wr.first_date is not None:
        data_fields["First Date of Production"] = f"{wr.first_date:%Y-%m-%d}"
    if wr.last_date is not None:
        data_fields["Last Date of Production"] = f"{wr.last_date:%Y-%m-%d}"
    if wr.record_access_date is not None:
        data_fields["Records Access Date"] = f"{wr.record_access_date:%Y-%m-%d}"
    for category in wr.registered_categories():
        drgroup = wr.date_ranges_by_category(category)
        drgroup_summary = summarize_date_range_group(
            drgroup, between=between, show_days=show_days, show_months=show_months
        )
        drgroup_summary["Description"] = category_descriptions.get(category, category)
        data_fields["Date Ranges"][category] = drgroup_summary
    return data_fields


def summarize_well_group(
    wg: WellGroup,
    category_descriptions: dict[str, str] = None,
    between="::",
    show_days: bool = False,
    show_months: bool = False,
) -> dict:
    """
    Summarize a well group's data fields into a dict.

    :param wg: The ``WellGroup`` instance to summarize.
    :param category_descriptions: (Optional) Pass a dict whose keys are
     the 'official' categories of date ranges registered to the well
     record; and whose values are a brief description of what that
     category means (e.g.,
     ``{'NO_PROD_IGNORE_SHUTIN'``: ``'No production (ignore shut-in)'}``).
    :param between: The string to go between the start/end date of each
     date range. (Default: ``'::'``).
    :param show_days: Whether to include the duration of each date range
     in days. (Default: ``False``)
    :param show_months: Whether to include the duration of each date
     range in calendar months. (Default: ``False``)
    """
    if category_descriptions is None:
        category_descriptions = {}
    summary = {
        "Well Count": len(wg.well_records),
        "API Numbers": [wr.api_num for wr in wg.well_records],
        "Earliest Reported Date": "No production reported",
        "Latest Reported Date": "No production reported",
        "Researched Gaps": {},
        "Well Records": [],
    }
    first_date = wg.find_first_date()
    if first_date is not None:
        summary["Earliest Reported Date"] = f"{first_date:%Y-%m-%d}"
    last_date = wg.find_last_date()
    if last_date is not None:
        summary["Latest Reported Date"] = f"{last_date:%Y-%m-%d}"
    for category, gaps in wg.researched_gaps.items():
        gaps_summary = summarize_date_range_group(
            gaps,
            between=between,
            show_days=show_days,
            show_months=show_months,
        )
        gaps_summary["Description"] = category_descriptions.get(category, category)
        summary["Researched Gaps"][category] = gaps_summary
    for wr in wg.well_records:
        wrsummary = summarize_well_record(
            wr,
            category_descriptions=category_descriptions,
            between=between,
            show_days=show_days,
            show_months=show_months,
        )
        summary["Well Records"].append(wrsummary)
    return summary


__all__ = [
    "summarize_date_range",
    "summarize_date_range_group",
    "summarize_well_record",
    "summarize_well_group",
]
