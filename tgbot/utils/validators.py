from config import settings


async def valid_name(db_data, name: str) -> str | None:
    name = name[:settings.LENGTH_NAME_LIMIT].strip()
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name
