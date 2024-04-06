import logging
from datetime import timedelta, date

import dotenv
from flask import Flask, request, jsonify, render_template
from markupsafe import Markup

from backend.database.mongodb_well_record_manager import (
    get_well_record_manager_for_environment,
)
from backend.data_analyzer.well_group import WellGroup
from backend.well_records.well_record import WellRecord
from backend.well_records.standard_categories import (
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs import STATE_CODE_SCRAPER_CONFIGS
from backend.database.well_record_manager import WellRecordManager
from backend.database.mongodb_well_record_manager import MongoDBWellRecordManager
from backend.summarizer.summarizer import summarize_well_group, summarize_well_record
from backend.utils.validate_api_num import validate_api_num
from backend.utils.state_codes import STATE_CODES

from config import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
)

CONFIGS = {
    "PROD": ProductionConfig(),
    "DEV": DevelopmentConfig(),
    "TEST": TestingConfig(),
}

CATEGORY_DESCRIPTIONS = {
    NO_PROD_IGNORE_SHUTIN: "No production (ignore shut-in)",
    NO_PROD_BUT_SHUTIN_COUNTS: "No production (shut-in counts as production)",
}

dotenv.load_dotenv()


def _get_config_from_state_code(state_code: str, logger: logging.Logger = None) -> dict:
    if state_code not in STATE_CODE_SCRAPER_CONFIGS.keys():
        logger.error(
            f"State code {state_code!r} ({STATE_CODES[state_code]}) not yet supported."
        )
        raise ValueError(
            f"State code {state_code!r} ({STATE_CODES[state_code]}) not yet supported."
        )
    return STATE_CODE_SCRAPER_CONFIGS[state_code]


def try_database_then_scraper(
    api_num: str,
    wrm: WellRecordManager,
    store_after: bool = True,
    max_record_age_in_days=3650,
    config_override: dict = None,
    logger: logging.Logger = None,
) -> WellRecord:
    """
    Get a ``WellRecord`` for the well with the specified API number.
    Will first attempt to pull it from the database that is configured
    in the ``WellRecordManager`` passed as ``wrm``. If no record exists
    for the well in the database, or if the record is older than the
    specified ``max_record_age_in_days``, will attempt to scrape it from
    the public records. Optionally, the scraped record will be stored to
    the database (or the existing outdated record will be updated) if
    ``store_after=True`` (the default behavior).

    By default, the scraper will be configured according to the state
    code in the API number (the first two digits). However, this can be
    overridden by passing an appropriate configuration dict to
    ``config_override``. If no ``config_override`` is provided and the
    requested API number is for a state not currently supported, a
    ``ValueError`` will be raised.

    :param api_num: The unique API number of the well to be pulled.
    :param wrm: The ``WellRecordManager`` in control of the database.
    :param store_after: (Optional) If the requested well must be
     scraped from public records, the resulting record will be added to
     the database if this is ``True`` (the default behavior).
    :param max_record_age_in_days: If the record that exists for this
     well in the database is older than this many days, will re-scrape
     public records for fresh records. (And if ``store_after=True``,
     then will update the database with the new record.)
    :param config_override: (Optional) The configuration dict to use for
     the scraper. If not provided, will use a preconfigured scraper for
     the state encoded in the API number (e.g., "05-xxx-xxxxx" will need
     a Colorado-specific scraper).
    :param logger: (Optional) A ``logging.Logger`` object.
    :return: A ``WellRecord`` object corresponding to the requested API
     number.
    """
    if not validate_api_num(api_num):
        raise ValueError("Invalid API number")
    state_code = api_num[:2]
    scraper_config = config_override
    well_record = wrm.find_well_record(api_num=api_num)
    if well_record is None:
        if logger is not None:
            logger.log(logging.INFO, f"No existing records for {api_num}; scraping.")
        if scraper_config is None:
            scraper_config = _get_config_from_state_code(state_code, logger)
        scraper = ScraperWellDataCollector.from_config(scraper_config)
        well_record = scraper.get_well_data(api_num)
        if store_after:
            if logger is not None:
                logger.log(logging.INFO, f"Inserting record for {api_num} into DB.")
            wrm.insert_well_record(well_record)
    elif (
        well_record.record_access_date is None
        or date.today()
        > well_record.record_access_date + timedelta(days=max_record_age_in_days)
    ):
        if logger is not None:
            logger.log(
                logging.INFO,
                f"Existing records for {api_num} "
                f"older than {max_record_age_in_days} days; scraping.",
            )
        if scraper_config is None:
            scraper_config = _get_config_from_state_code(state_code, logger)
        scraper = ScraperWellDataCollector.from_config(scraper_config)
        well_record = scraper.get_well_data(api_num)
        if store_after:
            if logger is not None:
                logger.log(logging.INFO, f"Updating record for {api_num} in DB.")
            wrm.update_well_record(well_record)
    else:
        if logger is not None:
            logger.log(logging.INFO, f"Existing record for {api_num} found in DB.")
    return well_record


def create_app(config: Config, environment_short_name: str = None) -> Flask:
    """

    :param config:
    :param environment_short_name: The short name of the environment.
     Default options are (``'PROD'``, ``'DEV'``, and ``'TEST'``,
     assuming they are configured in the ``.env`` file). If not
     specified as a parameter, this will attempt to pull the
     ``.ENVIRONMENT_SHORT_NAME`` attribute from the ``config`` object.
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(config)
    if environment_short_name is None:
        environment_short_name = config.ENVIRONMENT_SHORT_NAME

    wrm = get_well_record_manager_for_environment(environment_short_name)

    @app.route("/")
    def main():
        return """
         <form action="/collect_wells" method="POST">
             <input name="api_nums">
             <input type="submit" value="Submit!">
         </form>
         """

    def get_well_summary(api_num) -> dict:
        well_record = get_well_record(api_num)
        return summarize_well_record(
            well_record, category_descriptions=CATEGORY_DESCRIPTIONS, between=" :: "
        )

    @app.route("/well_record/<api_num>", methods=["GET"])
    def get_well_summary_as_json(api_num):
        summary = get_well_summary(api_num)
        return jsonify(summary)

    def get_well_group_summary(api_nums: list[str]) -> dict:
        """
        Collect well records, construct a well group, look for gaps,
        and summarize.
        :param api_nums: A list of API numbers of the wells to include
         in this group.
        :return: A summary dict for the well group (can be converted to
         json).
        """
        wg = WellGroup()
        for num in api_nums:
            well_record = try_database_then_scraper(num, wrm)
            wg.add_well_record(well_record)
        for category in wg.shared_categories():
            # This stores the researched category and resulting gaps to `wg.researched_gaps`.
            wg.find_gaps(category)
        summary = summarize_well_group(
            wg,
            category_descriptions=CATEGORY_DESCRIPTIONS,
            between=" :: ",
            show_days=True,
            show_months=True,
        )
        return summary

    @app.route("/well_group/<api_nums_separated_by_ampersand>", methods=["GET"])
    def get_well_group(api_nums_separated_by_ampersand):
        api_nums = api_nums_separated_by_ampersand.split("&")
        summary = get_well_group_summary(api_nums)
        return jsonify(summary)

    def get_well_record(api_num):
        return try_database_then_scraper(
            api_num,
            wrm,
            store_after=True,
            max_record_age_in_days=app.config["MAX_ACCEPTABLE_RECORD_AGE_IN_DAYS"],
            logger=app.logger,
        )

    @app.route("/collect_wells", methods=["POST"])
    def collect_wells_and_find_gaps():
        input_text = request.form.get("api_nums", "")
        api_nums = input_text.split(",")

        wg = WellGroup()
        for num in api_nums:
            well_record = get_well_record(num)
            wg.add_well_record(well_record)

        gaps = wg.find_gaps(NO_PROD_IGNORE_SHUTIN)
        output_str = f"for wells in {input_text}:"
        for gap in gaps:
            output_str += "<br>" + str(gap)
        return output_str

    def fill_well_group_report_template(well_group_summary: dict):
        """
        Fill out the ``well_group_report.html`` template with the
        ``summary`` dict for a given well group.
        :param well_group_summary:
        :return:
        """
        summary = well_group_summary
        well_simple_summaries = []
        for well in summary["Well Records"]:
            well_simple_summaries.append(f"{well['API Number']} ({well['Well Name']})")
        gaps_segments = []
        for category, data in summary["Researched Gaps"].items():
            s = Markup("<h4>") + data["Description"] + Markup("</h4>") + "\n"
            s += (
                Markup("<h5>")
                + f"Longest: {data['Longest (days)']} days"
                + Markup("</h5>")
                + "\n"
            )
            s += Markup("<ul>") + "\n"
            for date_range_string in data["Date Ranges"]:
                s += Markup("<li>") + date_range_string + Markup("</li>") + "\n"
            s += Markup("</ul>") + "\n"
            gaps_segments.append(s)
        if not gaps_segments:
            gaps_segments.append(
                Markup("<h4>") + "No gaps were researched." + Markup("</h4>")
            )
        return render_template(
            "well_group_report.html",
            well_simple_summaries=well_simple_summaries,
            first_date_of_production=summary["Earliest Reported Date"],
            last_date_of_production=summary["Latest Reported Date"],
            gaps_segments=gaps_segments,
        )

    return app


if __name__ == "__main__":
    app = create_app(CONFIGS["DEV"])
    app.run()
