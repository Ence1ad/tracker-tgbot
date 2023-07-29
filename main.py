from tgbot.bot_obj import bot
from telethon import TelegramClient, events


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello world')


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
