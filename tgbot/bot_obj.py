from telethon import TelegramClient

from config import tg_param

env = tg_param()
api_id = int(env['API_ID'])
api_hash = env['API_HASH']
bot_token = env['BOT_TOKEN']

bot = TelegramClient('tgbot', api_id=api_id, api_hash=api_hash).start(bot_token=bot_token)
