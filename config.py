from dotenv import dotenv_values
from aiogram.enums import ParseMode

from aiogram import Bot


def get_tg_bot(env_path='.env.tg.development'):
    tg_env = dotenv_values(dotenv_path=env_path)
    bot_token = tg_env['BOT_TOKEN']
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    my_bot = Bot(bot_token, parse_mode=ParseMode.HTML)
    return my_bot


bot = get_tg_bot()


def get_db_url(env_path='.env.db.development'):
    db_env = dotenv_values(dotenv_path=env_path)
    user = db_env["PGUSER"]
    password = db_env["PGPASSWORD"]
    host = db_env['PGHOST']
    port = db_env['PGPORT']
    dbname = db_env['DBNAME']

    url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    return url


db_url = get_db_url()
