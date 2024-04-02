from flask import Flask, request

from backend.data_analyzer.well_group import WellGroup
from backend.well_records.standard_categories import NO_PROD_IGNORE_SHUTIN
from backend.data_collector.well_data_scraper import ScraperWellDataCollector
from backend.data_collector.state_configs.colorado import COLORADO_CONFIG

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

    scraper = ScraperWellDataCollector.from_config(COLORADO_CONFIG)

    wg = WellGroup()
    for num in api_nums:
        new_data = scraper.get_well_data(api_num=num)
        wg.add_well_record(new_data)

    gaps = wg.find_gaps(NO_PROD_IGNORE_SHUTIN)
    output_str = f"for wells in {input_text}:"
    for gap in gaps:
        output_str += "<br>" + str(gap)
    return output_str


if __name__ == "__main__":
    app.run()
