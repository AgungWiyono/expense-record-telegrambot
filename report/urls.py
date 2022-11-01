from telegram.ext import CommandHandler

from report import bot_func

month_report_handler = CommandHandler("report", bot_func.this_month_report)

bot_handlers = [month_report_handler]
