from config import bot
from tgbot.handlers import start


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
