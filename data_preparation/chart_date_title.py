import datetime as dt
from dataclasses import dataclass


@dataclass
class DateTitle:
    year: int = dt.datetime.today().isocalendar().year
    week: int = dt.datetime.today().isocalendar().week

    @classmethod
    def _get_monday(cls) -> dt.date:
        cur_year_n_week = f"{cls.year}-W{cls.week}"
        monday: dt.date = dt.datetime.strptime(cur_year_n_week + '-1', "%Y-W%W-%w").date()
        return monday

    @classmethod
    def _get_sunday(cls) -> dt.date:
        sunday = cls._get_monday() + dt.timedelta(days=6)
        return sunday

    @classmethod
    def get_current_dow(cls) -> str:
        current_week_data = f"{cls._get_monday()} - {cls._get_sunday()}"
        return current_week_data
