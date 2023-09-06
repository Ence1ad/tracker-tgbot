from settings import LENGTH_NAME_LIMIT


async def valid_name(db_data, name: str) -> str | None:
    name = name[:LENGTH_NAME_LIMIT].strip()
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name
