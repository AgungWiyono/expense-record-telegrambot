import importlib

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram.ext import Dispatcher, Updater


def register_handler(dispatcher: Dispatcher, module_name: str):
    module = importlib.import_module(module_name)
    for handler in module.bot_handlers:
        dispatcher.add_handler(handler)


class Command(BaseCommand):
    help = "Run telegram bot polling"

    def handle(self, *args, **kwargs):
        TOKEN = settings.BOT_TOKEN
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        register_handler(dispatcher, "core.urls")
        register_handler(dispatcher, "expense.urls")

        updater.start_polling()
        updater.idle()
