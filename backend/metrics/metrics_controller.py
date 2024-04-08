from typing import Any
from datetime import datetime, timedelta


class MetricsController:
    def __init__(self, app=None):
        self.app = app
        self.creation_datetime = datetime.now()
        self.metrics: dict = {}

    @property
    def uptime_in_seconds(self):
        return (datetime.now() - self.creation_datetime).seconds

    @property
    def uptime(self):
        return timedelta(seconds=self.uptime_in_seconds)

    def new(self, field: str, data_type) -> None:
        self.metrics[field] = data_type()
        return None

    def get(self, field: str) -> Any:
        return self.metrics[field]

    def update(self, field: str, value: Any) -> None:
        self.metrics[field] = value
        return None

    def add_to(self, field: str, n: int) -> None:
        self.metrics[field] += n

    def increment(self, field: str) -> None:
        self.metrics[field] += 1
        return None

    def decrement(self, field: str) -> None:
        self.metrics[field] -= 1
        return None


__all__ = [
    "MetricsController",
]
