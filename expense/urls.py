from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler)

from expense import bot_func

text_filter = Filters.text & ~Filters.command

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("input", bot_func.start_input)],
    states={
        bot_func.NAME: [MessageHandler(text_filter, bot_func.name_processor)],
        bot_func.CATEGORY: [
            MessageHandler(text_filter, bot_func.category_processor)
        ],
        bot_func.AMOUNT: [
            MessageHandler(text_filter, bot_func.amount_processor)
        ],
        bot_func.RECEIPT: [
            MessageHandler(Filters.photo, bot_func.receipt_processor)
        ],
        bot_func.NOTE: [MessageHandler(text_filter, bot_func.note_processor)],
    },
    fallbacks=[CommandHandler("cancel", bot_func.cancel_input)],
)

bot_handlers = [conv_handler]
