from settings import LENGTH_ACTION_NAME_LIMIT


async def valid_name(db_data, name: str) -> str | None:
    db_data = db_data.all()
    print(db_data)
    for data in db_data:
        if str(name) in data:
            return None
    else:
        return name[:LENGTH_ACTION_NAME_LIMIT]
