from datetime import timedelta, date

import dotenv
from flask import Flask, request

from backend.database.mongodb_well_record_manager import (
    get_well_record_manager_for_environment,
)
from backend.data_analyzer.well_group import WellGroup
from backend.well_records.standard_categories import NO_PROD_IGNORE_SHUTIN
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG

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

dotenv.load_dotenv()


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

    max_record_age_in_days = 31

    wrm = get_well_record_manager_for_environment(environment_short_name)

    @app.route("/")
    def main():
        return """
         <form action="/collect_wells" method="POST">
             <input name="api_nums">
             <input type="submit" value="Submit!">
         </form>
         """

    @app.route("/collect_wells", methods=["POST"])
    def collect_wells_and_find_gaps():
        input_text = request.form.get("api_nums", "")
        api_nums = input_text.split(",")
        print(app.config)
        scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)

        wg = WellGroup()
        for num in api_nums:
            well_record = wrm.find_well_record(num)
            if well_record is None:
                print(f"scraping {num}")
                well_record = scraper.get_well_data(api_num=num)
                wrm.insert_well_record(well_record)
            elif (
                well_record.record_access_date is None
                or date.today()
                > well_record.record_access_date + timedelta(days=max_record_age_in_days)
            ):
                print(f"scraping {num} (existing record too old)")
                well_record = scraper.get_well_data(api_num=num)
                wrm.update_well_record(well_record)
            else:
                print(f"pulled {num} from database")
            wg.add_well_record(well_record)

        gaps = wg.find_gaps(NO_PROD_IGNORE_SHUTIN)
        output_str = f"for wells in {input_text}:"
        for gap in gaps:
            output_str += "<br>" + str(gap)
        return output_str

    return app


if __name__ == "__main__":
    app = create_app(CONFIGS["DEV"])
    app.run()
