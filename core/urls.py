from telegram.ext import CommandHandler

from core import bot_func

# echo_handler = MessageHandler(Filters.text & (~Filters.command), func.echo)
start_handler = CommandHandler("start", bot_func.start)

bot_handlers = [start_handler]
