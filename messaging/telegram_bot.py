import telebot
from settings.application_settings import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


def send_message(chat_id: str = settings.TELEGRAM_CHAT_ID, message: str = "Hello, World!"):
    bot.send_message(chat_id, message)
