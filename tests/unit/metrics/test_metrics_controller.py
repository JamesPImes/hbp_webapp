import unittest

from backend.metrics import MetricsController


class TestMetricsController(unittest.TestCase):

    def test_uptime_in_seconds(self):
        metrics = MetricsController()
        self.assertTrue(-1 < metrics.uptime_in_seconds < 5)

    def test_uptime(self):
        # .uptime is a `datetime.timedelta` object.
        metrics = MetricsController()
        self.assertTrue(-1 < metrics.uptime.seconds < 5)

    def test_new(self):
        metrics = MetricsController()
        metrics.new("Test 1", int)
        self.assertIsNotNone(metrics.metrics.get("Test 1", None))

    def test_update(self):
        metrics = MetricsController()
        metrics.new("Test 1", int)
        metrics.update("Test 1", 5)
        self.assertEqual(5, metrics.metrics.get("Test 1", None))

    def test_increment(self):
        metrics = MetricsController()
        metrics.new("Test 1", int)
        metrics.update("Test 1", 5)
        metrics.increment("Test 1")
        self.assertEqual(6, metrics.metrics.get("Test 1", None))

    def test_decrement(self):
        metrics = MetricsController()
        metrics.new("Test 1", int)
        metrics.update("Test 1", 5)
        metrics.decrement("Test 1")
        self.assertEqual(4, metrics.metrics.get("Test 1", None))

    def test_add_to(self):
        metrics = MetricsController()
        metrics.new("Test 1", int)
        metrics.update("Test 1", 5)
        metrics.add_to("Test 1", 4)
        self.assertEqual(9, metrics.metrics.get("Test 1", None))


if __name__ == "__main__":
    unittest.main()
