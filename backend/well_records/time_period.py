from datetime import date


class TimePeriod:
    """A period of time."""

    def __init__(self, start_date: date, end_date: date, category: str = None) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.category = category

    def duration_in_days(self) -> int:
        """Return the duration in days."""
        return (self.end_date - self.start_date).days


__all__ = [
    'TimePeriod',
]
