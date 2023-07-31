from dotenv import dotenv_values
from telethon import TelegramClient


def get_tg_bot():
    tg_env = dotenv_values(dotenv_path='.env.tg.development')
    api_id = int(tg_env['API_ID'])
    api_hash = tg_env['API_HASH']
    bot_token = tg_env['BOT_TOKEN']

    my_bot = TelegramClient('tgbot', api_id=api_id, api_hash=api_hash).start(bot_token=bot_token)
    return my_bot


bot = get_tg_bot()


def get_db_url():
    db_env = dotenv_values(dotenv_path='.env.db.development')
    user = db_env["PGUSER"]
    password = db_env["PGPASSWORD"]
    host = db_env['PGHOST']
    port = db_env['PGPORT']
    dbname = db_env['DBNAME']

    url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    return url


db_url = get_db_url()
