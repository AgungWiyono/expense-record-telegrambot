import os
import zipfile
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import pytz
import tablib  # type:ignore
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext

from expense import models


def compose_report(
    filename: str,
    old: bool = False,
) -> Tuple[Optional[bytes], List[str]]:
    refday = timezone.localdate()
    if old:
        first_day = refday.replace(day=1)
        refday = first_day - timedelta(days=1)

    year = refday.year
    month = refday.month
    records = models.Expense.objects.filter(
        created_at__year=year, created_at__month=month
    ).order_by("created_at")

    if not records:
        return None, []

    data = []
    filenames = []
    local_timezone = pytz.timezone("Asia/Jakarta")
    for index, record in enumerate(records):
        timestamp = record.created_at.astimezone(local_timezone).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        item = {
            "no": index + 1,
            "title": record.title,
            "category": record.category.name,
            "amount": float(record.amount),
            "receipt": record.receipt.file.name.split("/")[-1],
            "created_at": timestamp,
        }
        data.append(item)
        filenames.append(record.receipt.path)

    dataset = tablib.Dataset()
    dataset.headers = data[0].keys()
    for row in data:
        dataset.append(row.values())
    return dataset.export("xlsx"), filenames


def zip_images(reportname: str, excel_binary: bytes, filenames: List[str]):
    excel_name = reportname + ".xlsx"
    with open(excel_name, "wb") as fp:
        fp.write(excel_binary)

    zipname = f"{reportname}.zip"
    with zipfile.ZipFile(zipname, mode="w") as fp:
        fp.write(excel_name)
        for filename in filenames:
            fp.write(filename, "image/" + filename.split("/")[-1])

    return zipname


def delete_temp(report_name: str):
    os.remove(report_name + ".xlsx")
    os.remove(report_name + ".zip")


def this_month_report(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        return

    report_name = datetime.now().strftime("%Y%m%d%H%M%S")
    report, images = compose_report(report_name)
    if not report:
        message.reply_text("No report for this month.")
        return

    zipname = zip_images(report_name, report, images)
    with open(zipname, "rb") as fp:
        message.reply_document(fp.read(), filename=zipname)

    delete_temp(report_name)


def last_month_report(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        return

    report_name = datetime.now().strftime("%Y%m%d%H%M%S")
    report, images = compose_report(report_name, True)
    if not report:
        message.reply_text("No report for this month.")
        return

    zipname = zip_images(report_name, report, images)
    with open(zipname, "rb") as fp:
        message.reply_document(fp.read(), filename=zipname)

    delete_temp(report_name)
