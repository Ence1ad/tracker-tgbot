from dotenv import dotenv_values


# async def db_param(dotenv_filename='.env.db'):
#     return dotenv_values(dotenv_filename)


def tg_param(dotenv_filename: str = 'dev.tg.env') -> dict[str, str | None]:
    return dotenv_values(dotenv_filename)
