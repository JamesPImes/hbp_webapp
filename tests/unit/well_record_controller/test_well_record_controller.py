import unittest
import unittest.mock
from datetime import date

from backend.well_record_controller import WellRecordController
from backend.database import WellRecordDataGateway
from backend.well_record import WellRecord
from backend.data_collector import ScraperWellDataCollector
from backend.data_collector.state_configs import STATE_CODE_SCRAPER_CONFIGS


class TestWellRecordController(unittest.TestCase):

    def setUp(self) -> None:
        # Mock find() in database.
        gateway = WellRecordDataGateway()
        gateway.find = unittest.mock.MagicMock(
            return_value=WellRecord(
                api_num="05-234-56789", well_name="Pulled from database"
            )
        )
        # Mock insert()/update() in the database.
        gateway.insert = unittest.mock.MagicMock(return_value=None)
        gateway.update = unittest.mock.MagicMock(return_value=None)
        self.controller = WellRecordController(gateway=gateway)

        # Mock get_well_data() in scraper.
        colorado_collector = ScraperWellDataCollector.from_config(
            STATE_CODE_SCRAPER_CONFIGS["05"]
        )
        colorado_collector.get_well_data = unittest.mock.MagicMock(
            return_value=WellRecord(
                api_num="05-234-56789",
                well_name="Pulled from collector",
                record_access_date=date.today(),
            )
        )
        self.controller.register_collector("05", colorado_collector)

    def test_register_collector(self):
        dummy_collector = ScraperWellDataCollector.from_config(
            STATE_CODE_SCRAPER_CONFIGS["05"]
        )
        self.controller.register_collector("01", dummy_collector)
        self.assertTrue(("01", dummy_collector) in self.controller.collectors.items())

    def test_get_well_record_in_database(self):
        """
        Test ``get_well_record()`` when the result is in the database.
        :return:
        """
        found_well_record = self.controller.get_well_record("05-234-56789")
        self.assertEqual(found_well_record.api_num, "05-234-56789")

    def test_get_well_record_not_in_database(self):
        """
        Test ``get_well_record()`` when the result is not in the
        database.
        :return:
        """
        # Adjust mock of find() in database, so that the record is not found.
        self.controller.gateway.find = unittest.mock.MagicMock(return_value=None)
        found_well_record = self.controller.get_well_record("05-234-56789")
        self.assertEqual(found_well_record.well_name, "Pulled from collector")

    def test_get_well_record_too_old_in_database(self):
        """
        Test ``get_well_record()`` when the result is in the database,
        but it is too old.
        :return:
        """
        # Adjust mock of find() in database, so that the record is found,
        # but is too old.
        self.controller.gateway.find = unittest.mock.MagicMock(
            return_value=WellRecord(
                api_num="01-234-56789",
                well_name="Pulled from database",
                record_access_date=date(1999, 1, 1),
            )
        )
        # The well should be pulled from the collector, because the record found
        # in the database is too old.
        found_well_record = self.controller.get_well_record(
            "05-234-56789", max_record_age_in_days=100
        )
        self.assertEqual(found_well_record.well_name, "Pulled from collector")


if __name__ == "__main__":
    unittest.main()
