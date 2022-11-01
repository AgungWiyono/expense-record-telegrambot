import io
import os
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from expense import models

NAME, CATEGORY, AMOUNT, RECEIPT = range(4)


def create_record(data: dict):
    imagepath: str = data.pop("photo")
    filename = imagepath.split("/")[-1]
    with open(imagepath, "rb") as fp:
        imagebyte = fp.read()
    buffer = io.BytesIO(imagebyte)
    image_buffer = InMemoryUploadedFile(
        buffer, None, filename, "image/png", len(imagebyte), None
    )

    record = models.Expense(**data)
    record.receipt = image_buffer
    record.save()
    os.remove(imagepath)


def start_input(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    message.reply_text(
        "Enter the name of the new expense."
        "\nType /cancel to abort operation."
    )
    return NAME


def compose_category_choice() -> ReplyKeyboardMarkup:
    data = models.ExpenseCategory.objects.all()
    markup_choices = []

    markup_items = []
    for item in data:
        markup_items.append(item.name)
        if len(markup_items) == 2:
            markup_choices.append(markup_items)
            markup_items = []
    if markup_items:
        markup_choices.append(markup_items)

    markup = ReplyKeyboardMarkup(markup_choices, one_time_keyboard=True)
    return markup


def name_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    name = message.text

    user_data = context.user_data
    if user_data is None:
        return 0
    user_data["expense"] = {}
    user_data["expense"]["title"] = name

    markup = compose_category_choice()
    message.reply_text("Enter expense type: ", reply_markup=markup)

    return CATEGORY


def category_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    text = message.text

    category = models.ExpenseCategory.objects.filter(name=text).first()
    if not category:
        markup = compose_category_choice()
        message.reply_text(
            "Category is not valid. Please choose from one below.",
            reply_markup=markup,
        )
        return CATEGORY

    user_data = context.user_data
    if not user_data:
        return 0
    user_data["expense"]["category_id"] = category.id

    message.reply_text("Enter the amount: ")

    return AMOUNT


def amount_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    text = message.text

    user_data = context.user_data
    if not user_data:
        return 0
    user_data["expense"]["amount"] = text

    message.reply_text("Send the receipt: ")

    return RECEIPT


def receipt_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    if not message.from_user:
        return ConversationHandler.END

    photo = message.photo
    if not photo:
        return ConversationHandler.END

    user_data = context.user_data
    if not user_data:
        return 0

    photoname = str(int(datetime.now().timestamp()))
    photopath = f"/tmp/{photoname}.png"
    photo_file = photo[-1].get_file()
    photo_file.download(photopath)
    user_data["expense"]["photo"] = photopath
    create_record(user_data["expense"])
    del user_data["expense"]
    message.reply_text("Data has been saved.")
    return ConversationHandler.END


def cancel_input(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if not user_data:
        return 0
    del user_data["expense"]

    message = update.message
    if not message:
        return ConversationHandler.END

    message.reply_text("You've cancelled input process.")
    return ConversationHandler.END
