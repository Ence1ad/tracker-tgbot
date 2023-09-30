from sqlalchemy import Row
from aiogram import html
from config import settings


async def valid_name(db_data: list[Row], name: str) -> str | None:
    name = name and html.quote(name.strip())[:settings.LENGTH_NAME_LIMIT]
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name
