import os

import dotenv
from flask import Flask, request
from pymongo import MongoClient

from backend.database.mongodb_well_record_manager import MongoDBWellRecordManager
from backend.data_analyzer.well_group import WellGroup
from backend.well_records.standard_categories import NO_PROD_IGNORE_SHUTIN
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG


dotenv.load_dotenv(".env")

DATABASE_CONNECTION_STRING = os.environ.get("DATABASE_CONNECTION_STRING")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
WELL_RECORDS_COLLECTION_NAME = os.environ.get("WELL_RECORDS_COLLECTION_NAME")

CONNECTION = MongoClient(DATABASE_CONNECTION_STRING)

app = Flask(__name__)


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

    wrm = MongoDBWellRecordManager(
        connection=CONNECTION,
        db_name=DATABASE_NAME,
        well_records_collection_name=WELL_RECORDS_COLLECTION_NAME,
    )

    scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)

    wg = WellGroup()
    for num in api_nums:
        well_record = wrm.find_well_record(num)
        if well_record is None:
            well_record = scraper.get_well_data(api_num=num)
            print(f"scraping {num}")
            wrm.insert_well_record(well_record)
        else:
            print(f"pulled {num} from database")
        wg.add_well_record(well_record)

    gaps = wg.find_gaps(NO_PROD_IGNORE_SHUTIN)
    output_str = f"for wells in {input_text}:"
    for gap in gaps:
        output_str += "<br>" + str(gap)
    return output_str


if __name__ == "__main__":
    app.run()
