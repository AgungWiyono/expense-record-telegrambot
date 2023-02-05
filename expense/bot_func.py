import io
import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from expense import models

NAME, CATEGORY, AMOUNT, RECEIPT, NOTE = range(5)


def create_record(data: dict):
    imagepath: str = data.pop("photo")
    filename = imagepath.split("/")[-1]
    ext = filename.split(".")[1]
    with open(imagepath, "rb") as fp:
        imagebyte = fp.read()
    buffer = io.BytesIO(imagebyte)
    image_buffer = InMemoryUploadedFile(
        buffer, None, filename, f"image/{ext}", len(imagebyte), None
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
        "Masukkan nama pengeluaran.\nKetikkan /cancel untuk membatalkan."
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
    choice_text = (
        "Silakan pilih kategori pengeluaran.\n"
        "Jika tidak tersedia silakan batalkan input saat ini dengan /cancel"
        "kemudian buat kategori baru pada situs "
        "https://expensebot.sandboxindonesia.id/admin."
    )
    message.reply_text(choice_text, reply_markup=markup)

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
            "Kategori tidak tersedia.Silakan pilih dari yang ada dibawah ini.",
            reply_markup=markup,
        )
        return CATEGORY

    user_data = context.user_data
    if not user_data:
        return 0
    user_data["expense"]["category_id"] = category.id

    message.reply_text("Masukkan jumlah pengeluaran (hanya angka): ")

    return AMOUNT


def amount_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    text = message.text
    if not text:
        message.reply_text("Tidak ada angka diterima.")
        return AMOUNT
    if not text.isdigit():
        message.reply_text("Hanya menerima input angka.")
        return AMOUNT

    user_data = context.user_data
    if not user_data:
        return 0
    user_data["expense"]["amount"] = text

    receipt_text = (
        "Kirimkan resi atau nota dalam bentuk gambar."
        "Jika menggunakan telegram non-mobile, centang opsi kompres gambar."
    )
    message.reply_text(receipt_text)

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

    photo_file = photo[-1].get_file()
    photo_file.download()
    photopath = photo_file.file_path
    if not photopath:
        message.reply_text("Photo tidak dapat diterima.")
        message.reply_text("Silakan upload ulang!")
        return RECEIPT
    user_data["expense"]["photo"] = photopath.split("/")[-1]

    message.reply_text("Silahkan masukkan catatan: ")
    return NOTE


def note_processor(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message:
        return ConversationHandler.END
    if not message.from_user:
        return ConversationHandler.END
    text = message.text

    user_data = context.user_data
    if not user_data:
        return 0

    user_data["expense"]["note"] = text

    create_record(user_data["expense"])
    del user_data["expense"]
    message.reply_text("Data telah tersimpan.")
    return ConversationHandler.END


def cancel_input(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if not user_data:
        return 0
    del user_data["expense"]

    message = update.message
    if not message:
        return ConversationHandler.END

    message.reply_text("Proses input berhasil dibatalkan.")
    return ConversationHandler.END
