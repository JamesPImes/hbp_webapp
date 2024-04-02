"""
Scrape well data from websites that provide monthly tabular production
data that can be accessed via a URL that encodes a unique identifier for
each well.

For example, the ECMC is the agency that oversees and regulates
production of oil and gas in Colorado. Through their website,
<https://ecmc.state.co.us/>, production records for a given well can be
accessed via a URL that follows this format:

https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code={0}&api_seq_num={1}

...where ``api_county_code`` and ``api_seq_num`` are part of the well's API
number (a unique identifier in the format ``05-987-12345``, where the
middle section ``987`` is the ``api_county_code`` and the last part
``12345`` is the ``api_seq_num``. (This example is a fake API number.)

.. note:

    This class relies heavily on a previous project I created for
    scraping and summarizing production data. See details here:
    https://github.com/JamesPImes/og_production_analyzer
"""

from __future__ import annotations
from datetime import date
from calendar import monthrange
from typing import Callable

import pandas as pd
from production_analyzer import ProductionAnalyzer, DataLoader, HTMLLoader

from ..well_records.well_record import WellRecord
from ..well_records.date_range import DateRange, DateRangeGroup
from ..well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)
from .well_data_collector import WellDataCollector


class ScraperWellDataCollector(WellDataCollector):
    def __init__(
        self,
        prod_url_template,
        date_col: str,
        oil_prod_col: str,
        gas_prod_col: str,
        days_produced_col: str = None,
        status_col: str = None,
        shutin_codes: list[str] = None,
        oil_prod_min: int = 0,
        gas_prod_min: int = 0,
        url_component_function: Callable = None,
        auth=None,
    ) -> None:
        """

        :param prod_url_template: A template for the URL of the webpage
         that contains production data for a given well. For example,
         the Colorado's ECMC website allows for production records to be
         accessed at this URL:

         ``https://ecmc.state.co.us/cogisdb/Facility/Production?api_county_code={0}&api_seq_num={1}``

         ...where ``api_county_code`` and ``api_seq_num`` are part of
         the well's API number (a unique identifier in the format
         ``05-987-12345``, where the middle section ``987`` is the
         ``api_county_code`` and the last part ``12345`` is the
         ``api_seq_num``. (This example is a fake API number.)

        :param date_col: The header for the date column in the original
         tabular data as provided on the website.
        :param oil_prod_col: The header for the column that contains
         the monthly oil production.
        :param gas_prod_col: The header for the column that contains
         the monthly gas production.
        :param days_produced_col: The header for the column that
         indicates how many days the well was active during the month.
         (Not all states provide this data, in which case, this should
         be ``None``.)
        :param status_col: The header for the column that indicates the
         "status" of the well during each month. (Not all states provide
         this data, in which case, this should be ``None``.)
        :param shutin_codes: A list of status codes that should be
         considered as "shut-in". (Not all states provide this data, in
         which case, this should be ``None`` or an empty list.)
        :param oil_prod_min: Minimum reported gas (typically in BBLs) to
         be considered producing. Defaults to 0 (i.e., any oil counts).
        :param gas_prod_min: Minimum reported gas (typically in MCF) to
         be considered producing. Defaults to 0 (i.e., any gas counts).
        :param url_component_function: A function that will take in all
         parameters from the ``.get_well_data()`` method as a
         ``**kwargs`` dict and return a list of the necessary components
         to be plugged into the ``prod_url_template``. For example,
         Colorado's ECMC website requires the 2nd and 3rd parts of a
         unique API number, which is in the format ``'05-987-12345'``. A
         ``url_component_function`` should take in a dict (named
         ``kw``), pull ``kw['api_num']``, and return a list of two
         strings, such as ``['987', '12345']``.
        :param auth: Only needed for websites that require
         authorization. For example, North Dakota's DMR website requires
         a subscription to access production records; and ``auth`` would
         need to be ``auth=auth.HTTPBasicAuth(user, password)`` (must
         first ``import auth``). On the other hand, Colorado's ECMC
         website provides all data for free to the public.
        """
        super().__init__()
        self.prod_url_template = prod_url_template
        self.date_col = date_col
        self.oil_prod_col = oil_prod_col
        self.gas_prod_col = gas_prod_col
        self.days_produced_col = days_produced_col
        self.status_col = status_col
        self.auth = auth
        self.shutin_codes = shutin_codes
        self.oil_prod_min = oil_prod_min
        self.gas_prod_min = gas_prod_min
        self.url_component_function: Callable = url_component_function

    @staticmethod
    def from_config(config: dict) -> ScraperWellDataCollector:
        """Get a new scraper from a config dictionary."""
        return ScraperWellDataCollector(**config)

    def set_auth(self, auth) -> None:
        """
        Set the ``auth`` for the scraper. (Only required for some
        states.)
        """
        self.auth = auth

    def set_url_component_function(self, url_component_function: Callable) -> None:
        """
        Set the ``url_component_function`` for this scraper. (Reference
        the documentation for the ``url_component_function`` parameter
        at init for further details.)

        :param url_component_function:
        :return:
        """
        self.url_component_function = url_component_function

    def get_html_scraper(self):
        """
        Get an ``HTMLLoader`` object that is configured according to
        this scraper.

        If ``auth`` is required for this state, ensure that it is
        configured prior to calling this method.
        """
        html_scraper = HTMLLoader(
            prod_url_template=self.prod_url_template,
            date_col=self.date_col,
            oil_prod_col=self.oil_prod_col,
            gas_prod_col=self.oil_prod_col,
            days_produced_col=self.days_produced_col,
            status_col=self.status_col,
            auth=self.auth,
        )
        return html_scraper

    def get_data_loader(self) -> DataLoader:
        """
        Get a ``DataLoader`` object that is configured according to this
        scraper.
        """
        data_loader = DataLoader(
            date_col=self.date_col,
            oil_prod_col=self.oil_prod_col,
            gas_prod_col=self.gas_prod_col,
            days_produced_col=self.days_produced_col,
            status_col=self.status_col,
        )
        return data_loader

    def get_analyzer(self, prod_df: pd.DataFrame) -> ProductionAnalyzer:
        """
        Get a ``ProductionAnalyzer`` object that is configured according
        to this scraper.
        """
        analyzer = ProductionAnalyzer(
            df=prod_df,
            date_col=self.date_col,
            oil_prod_col=self.oil_prod_col,
            gas_prod_col=self.gas_prod_col,
            days_produced_col=self.days_produced_col,
            status_col=self.status_col,
            shutin_codes=self.shutin_codes,
            oil_prod_min=self.oil_prod_min,
            gas_prod_min=self.gas_prod_min,
        )
        return analyzer

    def get_production_data_for_well(self, url) -> pd.DataFrame | None:
        """
        Collect the production records from the specified URL as a
        ``DataFrame``. If no production is reported at the URL, this
        will return ``None``.

        If ``auth`` is required for this state, ensure that it is
        configured prior to calling this method.

        :param url: The URL to scrape.
        :return:
        """
        html_scraper = self.get_html_scraper()
        html = html_scraper.get_html(url)
        return html_scraper.get_production_data_from_html(html)

    def get_url(self, **kw) -> str:
        """
        Get the URL of the production record a given well, based on the
        contents of the ``kw`` dict. (Exactly how the URL is calculated
        depends on the URL template stored to ``.prod_url_template`` and
        the function ``.url_component_function()`` that is configured
        for this object.)
        :param kw:
        :return:
        """
        if self.url_component_function is None:
            raise RuntimeError(
                "Cannot determine URL components. "
                "Ensure `url_component_function` is configured."
            )
        components = self.url_component_function(**kw)
        return self.prod_url_template.format(*components)

    def get_well_data(self, api_num: str, well_name: str = None, **kw) -> WellRecord:
        """
        Get a ``WellRecord`` for the well, based on the specified API
        number, well name, and any other specified kwargs.

        To load from a specific URL, pass ``url=som_url`` as a kwarg,
        which will ignore

        :param api_num: The unique API number for this well.
        :param well_name: The well name for this well.
        :param url: Load from this URL exactly, overriding any other
         configured behavior that might try to determine the URL
         automatically.
        :param kw: Any other keyword arguments that might be necessary
         (e.g., for the ``.url_component_function()`` configured for a
         given instance of this class).
        :return: A ``WellRecord`` showing the configured date ranges
         (e.g., gaps in production).
        """
        if "api_num" not in kw.keys():
            kw["api_num"] = api_num
        if "well_name" not in kw.keys():
            kw["well_name"] = well_name
        # Pull the provided URL from the kwargs, if they exist. Otherwise,
        # determine the URL from `.get_url()` method defined for this class.
        url = kw.get("url", self.get_url(**kw))
        raw_prod_df = self.get_production_data_for_well(url)
        if raw_prod_df is None:
            # No production found for this well.
            well_record = WellRecord(
                api_num, well_name, record_access_date=date.today()
            )
            well_record.register_empty_category(NO_PROD_IGNORE_SHUTIN)
            if None not in (self.shutin_codes, self.status_col):
                well_record.register_empty_category(NO_PROD_BUT_SHUTIN_COUNTS)
            return well_record

        # Extract first/last production dates.
        analyzer = self.get_analyzer(raw_prod_df)
        first_date_raw = analyzer.prod_df[self.date_col].min()
        first_date = date(first_date_raw.year, first_date_raw.month, first_date_raw.day)
        last_date_raw = analyzer.prod_df[self.date_col].max()
        # Convert the last date to the date occurring at the end of the month.
        _, last_day_in_month = monthrange(last_date_raw.year, last_date_raw.month)
        last_date = date(last_date_raw.year, last_date_raw.month, last_day_in_month)

        well_record = WellRecord(
            api_num=api_num,
            well_name=well_name,
            first_date=first_date,
            last_date=last_date,
            record_access_date=date.today(),
        )

        well_record.register_empty_category(NO_PROD_IGNORE_SHUTIN)
        gaps_ignore_si = analyzer.gaps_by_production_threshold(
            shutin_as_producing=False
        )
        gaps_ignore_si_drgroup = _gaps_df_to_daterangegroup(gaps_ignore_si)
        for dr in gaps_ignore_si_drgroup:
            well_record.register_date_range(dr, category=NO_PROD_IGNORE_SHUTIN)

        if None not in (self.shutin_codes, self.status_col):
            well_record.register_empty_category(NO_PROD_BUT_SHUTIN_COUNTS)
            gaps_allow_si = analyzer.gaps_by_production_threshold(
                shutin_as_producing=True
            )
            gaps_allow_si_drgroup = _gaps_df_to_daterangegroup(gaps_allow_si)
            for dr in gaps_allow_si_drgroup:
                well_record.register_date_range(dr, category=NO_PROD_BUT_SHUTIN_COUNTS)

        return well_record


def _gaps_df_to_daterangegroup(gaps_df: pd.DataFrame) -> DateRangeGroup:
    """
    INTERNAL USE:

    Convert a gaps dataframe (as generated by a ``ProductionAnalyzer``)
    to an equivalent ``DateRangeGroup``.

    :param gaps_df:
    :return:
    """
    group = DateRangeGroup()
    for _, row in gaps_df.iterrows():
        start_date = row["start_date"].date()
        end_date = row["end_date"].date()
        date_range = DateRange(start_date, end_date)
        group.add_date_range(date_range)
    return group


__all__ = [
    "ScraperWellDataCollector",
]
