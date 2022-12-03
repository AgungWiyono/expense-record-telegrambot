from typing import Optional

from telegram import Chat, Message, Update
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext):
    print("Test")
    chat: Optional[Chat] = update.effective_chat
    if not chat:
        return
    context.bot.send_message(chat_id=chat.id, text="Hi, I'm Expense Bot")


def echo(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.message
    if not chat or not message:
        return

    message_text = message.text
    if not message_text:
        return
    return_message = message_text.upper()

    context.bot.send_message(chat_id=chat.id, text=return_message)
