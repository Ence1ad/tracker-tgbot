import datetime as dt
from dataclasses import dataclass


@dataclass
class DateTitle:
    """Data class for working with dates and week numbers.

    Attributes
    ----------
        year (int): The current year.
        week (int): The current ISO week number.

    Methods
    -------
        _get_monday(): Get the date of the Monday in the current week.
        _get_sunday(): Get the date of the Sunday in the current week.
        get_current_dow(): Get a string representing the current week's date range
        (Monday - Sunday).
    """

    year: int = dt.datetime.today().isocalendar().year
    week: int = dt.datetime.today().isocalendar().week

    @classmethod
    def _get_monday(cls: type['DateTitle']) -> dt.date:
        """Get the date of the Monday in the current week.

        :return: date: The date of the Monday.
        """
        cur_year_n_week = f"{cls.year}-W{cls.week}"
        monday: dt.date = dt.datetime.strptime(cur_year_n_week + '-1',
                                               "%Y-W%W-%w").date()
        return monday

    @classmethod
    def _get_sunday(cls: type['DateTitle']) -> dt.date:
        """Get the date of the Sunday in the current week.

        :return:  date: The date of the Sunday.
        """
        sunday = cls._get_monday() + dt.timedelta(days=6)
        return sunday

    @classmethod
    def get_current_dow(cls: type['DateTitle']) -> str:
        """Get a string representing the current week's date range (Monday - Sunday).

        :return: str: A string in the format "YYYY-MM-DD - YYYY-MM-DD".
        """
        current_week_data = f"{cls._get_monday()} - {cls._get_sunday()}"
        return current_week_data
