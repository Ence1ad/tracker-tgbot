import datetime as dt
from dataclasses import dataclass
from typing import Type


@dataclass
class DateTitle:
    year: int = dt.datetime.today().isocalendar().year
    week: int = dt.datetime.today().isocalendar().week

    @classmethod
    def _get_monday(cls: Type['DateTitle']) -> dt.date:
        """
        The _get_monday function is a class method that returns the date of the Monday
        of the week in which this DateTitle object's year and week are found.


        :param cls: Type['DateTitle']: Specify the class type of the object that is being passed in
        :return: The date of the monday of the week in which
        """
        cur_year_n_week = f"{cls.year}-W{cls.week}"
        monday: dt.date = dt.datetime.strptime(cur_year_n_week + '-1', "%Y-W%W-%w").date()
        return monday

    @classmethod
    def _get_sunday(cls: Type['DateTitle']) -> dt.date:
        """
        The _get_sunday function is a class method that returns the date of the Sunday
        of the week in which this DateTitle object's date falls. It does so by calling
        the _get_monday function, and then adding 6 days to it.

        :param cls: Type['DateTitle']: Specify the class that is being passed in
        :return: The date of the sunday in the week that contains
        """
        sunday = cls._get_monday() + dt.timedelta(days=6)
        return sunday

    @classmethod
    def get_current_dow(cls: Type['DateTitle']) -> str:
        """
        The get_current_dow function returns a string representing the current week's date range.

        :param cls: Type['DateTitle']: Pass the class datetitle to the function
        :return: The current week's date range
        """
        current_week_data = f"{cls._get_monday()} - {cls._get_sunday()}"
        return current_week_data
