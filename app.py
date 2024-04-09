import logging
from datetime import timedelta, date, datetime

import dotenv
from flask import Flask, request, jsonify, render_template
from markupsafe import Markup
from pymongo import MongoClient

from backend.data_analyzer.well_group import WellGroup
from backend.well_records.well_record import WellRecord
from backend.well_records.standard_categories import (
    CATEGORY_DESCRIPTIONS,
    NO_PROD_IGNORE_SHUTIN,
    NO_PROD_BUT_SHUTIN_COUNTS,
)
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs import STATE_CODE_SCRAPER_CONFIGS
from backend.database.mongodb_well_record_data_gateway import (
    MongoDBWellRecordDataGateway,
)
from backend.summarizer.summarizer import summarize_well_group, summarize_well_record
from backend.well_record_controller import WellRecordController
from backend.utils.validate_api_num import validate_api_num
from backend.utils.state_codes import STATE_CODES
from backend.metrics import MetricsController

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

COLLECTORS = {
    "05": ScraperWellDataCollector.from_config(STATE_CODE_SCRAPER_CONFIGS["05"]),
}

dotenv.load_dotenv()


def create_app(config: Config) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(config)
    # Construct the WellRecordController.
    if config.MONGO_CONNECTION_STRING is None and config.MONGO_URI is None:
        raise RuntimeError("The database must be configured.")
    connection_string = config.MONGO_CONNECTION_STRING
    if connection_string is None:
        connection_string = config.MONGO_URI.format(
            username=config.MONGO_USER, password=config.MONGO_PASS
        )
    connection = MongoClient(connection_string)
    gateway = MongoDBWellRecordDataGateway(
        connection=connection,
        db_name=config.DATABASE_NAME,
        well_records_collection_name=config.WELL_RECORDS_COLLECTION,
    )
    well_record_controller = WellRecordController(
        gateway=gateway, collectors=COLLECTORS, logger=app.logger
    )

    # Register metrics.
    app.metrics = MetricsController(app)
    app.metrics.new("request_count", data_type=int)
    app.metrics.new("well_record_count", data_type=int)
    app.metrics.new("total_record_access_time_in_milliseconds", data_type=int)

    @app.route("/")
    def main():
        app.metrics.increment("request_count")
        return render_template("api_entry_form.html")

    @app.route("/get_report", methods=["POST"])
    def generate_well_group_report_from_request():
        app.metrics.increment("request_count")
        api_nums_raw = request.form.get("api_nums", "")
        api_nums = api_nums_raw.replace(" ", "").split(",")
        summary = get_well_group_summary(api_nums)
        return fill_well_group_report_template(summary)

    def get_well_summary(api_num) -> dict:
        well_record = get_well_record(api_num)
        return summarize_well_record(
            well_record, category_descriptions=CATEGORY_DESCRIPTIONS, between=" :: "
        )

    @app.route("/well_record/<api_num>", methods=["GET"])
    def get_well_summary_as_json(api_num):
        app.metrics.increment("request_count")
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
        for api_num in api_nums:
            well_record = get_well_record(api_num)
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

    @app.route("/well_group/<api_nums_separated_by_comma>", methods=["GET"])
    def get_well_group_summary_as_json(api_nums_separated_by_comma):
        app.metrics.increment("request_count")
        api_nums = api_nums_separated_by_comma.split(",")
        summary = get_well_group_summary(api_nums)
        return jsonify(summary)

    def get_well_record(api_num: str, well_name: str = None, **kw) -> WellRecord:
        """
        Get a well record.
        :param api_num:
        :param well_name:
        :param kw:
        :return:
        """
        ts1 = datetime.now()
        well_record = well_record_controller.get_well_record(
            api_num,
            max_record_age_in_days=Config.MAX_RECORD_AGE_IN_DAYS,
            well_name=well_name,
            store_after=True,
            **kw,
        )
        ts2 = datetime.now()
        if well_record is not None:
            app.metrics.increment("well_record_count")
            app.metrics.add_to(
                "total_record_access_time_in_milliseconds",
                round((ts2 - ts1).microseconds / 1000),
            )
        return well_record

    @app.route("/well_group_report", methods=["GET"])
    def well_group_report_from_url_parameter():
        """
        Fill in the well group report template for the API numbers
        provided in the URL.

        Ex: ``'/well_group_report?api_nums=05-123-45678,05-987-65432'``

        :return:
        """
        app.metrics.increment("request_count")
        api_nums = request.args.get("api_nums").split(",")
        summary = get_well_group_summary(api_nums)
        return fill_well_group_report_template(summary)

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
            s = Markup("<h4><u>") + data["Description"] + Markup("</u></h4>") + "\n"
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

    @app.route("/metrics")
    def metrics():
        """Basic metrics."""
        # Do not increment request_count for '/metrics' request.
        well_record_count = app.metrics.get("well_record_count")
        total_access_time = app.metrics.get("total_record_access_time_in_milliseconds")
        avg_access_time = "n/a"
        if well_record_count != 0:
            avg_access_time = int(total_access_time / well_record_count)
        fields = [
            f"Uptime: {app.metrics.uptime}",
            f"Requests: {app.metrics.get('request_count')}",
            f"Well records pulled: {well_record_count}",
            f"Avg well record access time (ms): {avg_access_time}",
        ]
        try:
            well_record_controller.gateway.find("dummy")
        except:
            return "500", f"Database could not be reached."
        return "200", "\n".join(fields)

    return app


if __name__ == "__main__":
    app = create_app(CONFIGS["DEV"])
    app.run()
