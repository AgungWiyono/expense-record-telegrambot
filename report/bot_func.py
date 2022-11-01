from datetime import timedelta
from typing import Optional

import tablib  # type:ignore
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext

from expense import models


def compose_report(old: bool = False) -> Optional[bytes]:
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
        return None

    data = []
    for index, record in enumerate(records):
        item = {
            "no": index + 1,
            "title": record.title,
            "category": record.category.name,
            "amount": float(record.amount),
            "created_at": record.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        }
        data.append(item)

    dataset = tablib.Dataset()
    dataset.headers = data[0].keys()
    for row in data:
        dataset.append(row.values())
    return dataset.export("xlsx")


def this_month_report(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        return

    report = compose_report()
    if not report:
        message.reply_text("No report for this month.")
        return
    message.reply_document(report, filename="report.xlsx")


def last_month_report(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        return

    report = compose_report(True)
    if not report:
        message.reply_text("No report for last month.")
        return
    message.reply_document(report, filename="report.xlsx")
