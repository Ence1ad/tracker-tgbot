from sqlalchemy import Row
from aiogram import html
from config import settings


async def valid_name(db_data: list[Row], name: str) -> str | None:
    """
    The valid_name function takes a list of Row objects and a string as arguments.

    :param db_data: list[Row]: Pass in a list of rows from the database
    :param name: str: Pass in the name that is being checked
    :return: A string or none
    """
    name = name and html.quote(name.strip())[:settings.LENGTH_NAME_LIMIT]
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name
