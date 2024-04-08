import logging
from datetime import date, timedelta

from backend.database import WellRecordDataGateway
from backend.data_collector import WellDataCollector
from backend.well_records import WellRecord
from backend.data_analyzer import WellGroup
from backend.utils import validate_api_num


class WellRecordController:
    """
    A controller for collecting well records from a database or public
    records.
    """

    def __init__(
        self,
        gateway: WellRecordDataGateway,
        collectors: dict[str, WellDataCollector] = None,
        logger: logging.Logger = None,
    ) -> None:
        if collectors is None:
            collectors = {}
        self.gateway = gateway
        self.collectors: dict[str, WellDataCollector] = collectors.copy()
        self.logger: logging.Logger = logger

    def register_collector(self, state_code: str, collector: WellDataCollector) -> None:
        """
        Register a ``WellDataCollector`` for a given state code (e.g.,
        a ``ScraperWellDataCollector`` for state code ``'05'``, for
        Colorado).
        :param state_code: The state code (the first 2 digits of an API
         number).
        :param collector: A ``WellDataCollector`` or one of its
         subclasses to use for collecting records for the state
         represented by the provided state code.
        :return: None
        """
        self.collectors[state_code] = collector

    def get_well_record(
        self,
        api_num: str,
        well_name: str = None,
        max_record_age_in_days=3650,
        store_after: bool = True,
        **kw,
    ) -> WellRecord | None:
        """
        Get a ``WellRecord`` for the well with the specified API number.
        Will first attempt to pull it from the database that is
        configured in the ``WellRecordDataGateway``. If no record exists
        for the well in the database, or if the record is older than the
        specified ``max_record_age_in_days``, will attempt to scrape it
        from the public records. Optionally, the scraped record will be
        stored to the database (or the existing outdated record will be
        updated) if ``store_after=True`` (the default behavior).

        Ensure that a collector is registered to this controller for
        a given state code before passing it to this method, otherwise a
        ``ValueError`` will be raised.

        :param api_num: The unique API number of the well to be pulled.
        :param well_name: (Optional) The name to use for the well
         record. (Will not overwrite any record pulled from the
         database.)
        :param max_record_age_in_days: If the record that exists for
         this well in the database is older than this many days, will
         re-collect public records for fresh records. (And if
         ``store_after=True``, then will update the database with the
         new record.)
        :param store_after: (Optional) If the requested well must be
         pulled from public records, the resulting record will be added
         to the database if this is ``True`` (the default behavior).
        :param kw: Other keyword argument to pass to the collector's
         ``.get()`` method.
        :return: The well record, if found; otherwise, ``None``.
        """
        if not validate_api_num(api_num):
            msg = "Invalid API number."
            if self.logger:
                self.logger.error(msg)
            raise ValueError(msg)
        existing_record = self.gateway.find(api_num, **kw)
        too_old = False
        try:
            record_age = existing_record.record_access_date
            too_old = date.today() > record_age + timedelta(days=max_record_age_in_days)
        except (TypeError, AttributeError):
            pass
        if existing_record is not None and not too_old:
            if self.logger is not None:
                self.logger.log(
                    logging.INFO, f"Well record for {api_num!r} found in database."
                )
            return existing_record
        state_code = api_num[:2]
        collector = self.collectors.get(state_code, None)
        if collector is None:
            msg = f"No collector registered for state code {state_code!r}."
            if self.logger is not None:
                self.logger.error(msg)
            raise RuntimeError(msg)
        new_record = collector.get_well_data(api_num=api_num, well_name=well_name, **kw)
        if new_record is not None:
            msg = f"Well record for {api_num!r} collected"
            if store_after:
                self.gateway.insert(new_record, **kw)
                msg += " and added to the database"
            if too_old:
                msg += (
                    f" (previous record was older than {max_record_age_in_days} days)"
                )
            msg += "."
            if self.logger is not None:
                self.logger.log(logging.INFO, msg)
        else:
            if self.logger is not None:
                self.logger.log(
                    logging.INFO, f"Well record for {api_num!r} could not be collected."
                )
        return new_record

    def get_well_group(
        self,
        api_nums: list[str],
        well_names: list[str] = None,
        max_record_age_in_days=3650,
        store_after: bool = True,
        **kw,
    ) -> WellGroup:
        """
        Get a well group from the list of ``api_nums``. If well names
        are provided for each well, the ``well_names`` list should be
        equal in length to ``api_nums``, or a ``ValueError`` will be
        raised.

        :param api_nums: A list of unique API numbers of the wells to be
         pulled.
        :param well_names: (Optional) A list of the names to use for the
         well records. (Will not overwrite any record pulled from the
         database.)
        :param max_record_age_in_days: If a record that exists for a
         requested well in the database is older than this many days,
         will re-collect public records for fresh records. (And if
         ``store_after=True``, then will update the database with the
         new record.)
        :param store_after: (Optional) If a requested well must be
         pulled from public records, the resulting record will be added
         to the database if this is ``True`` (the default behavior).
        :param kw: Other keyword argument to pass to the collector's
         ``.get()`` method.

         .. warning::
            If the collector for a given state requires the use of the
            keyword arguments (other than ``api_num``) for individual
            wells (e.g., if a different unique number is required for
            each well), this method should not be used for that state.
            Instead, construct the ``WellGroup`` by calling
            ``.get_well_record()`` for each well.

        :return: A ``WellGroup`` with the requested wells.
        """
        if well_names is None:
            well_names = [None] * len(api_nums)
        if len(api_nums) != len(well_names):
            raise ValueError(
                "If `well_names` are specified, must be same count as `api_nums`."
            )
        wg = WellGroup()
        for api_num, well_name in zip(api_nums, well_names):
            wr = self.get_well_record(
                api_num=api_num,
                well_name=well_name,
                store_after=store_after,
                max_record_age_in_days=max_record_age_in_days,
                **kw,
            )
            wg.add_well_record(wr)
        return wg


__all__ = [
    "WellRecordController",
]
