from sqlalchemy import Sequence
from aiogram import html
from config import settings


async def valid_name(db_data: Sequence, name: str) -> str | None:
    """Validate a name to ensure it's unique and within length limits.

    :param db_data: db_data Sequence: A list of database rows containing existing names
     for comparison.
    :param name: str: The name to be validated.
    :return: str or None: If the name is valid and unique, it's returned with
    leading/trailing whitespace removed and truncated to the length specified in the
    settings (settings.LENGTH_NAME_LIMIT). If the name is not valid (e.g., not unique),
    None is returned.
    """
    name = name and html.quote(name.strip())[:settings.LENGTH_NAME_LIMIT]
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name
