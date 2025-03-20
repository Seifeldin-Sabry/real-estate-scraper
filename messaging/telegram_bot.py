import telebot
from settings.application_settings import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
