from django.contrib import admin

from expense import models


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "created_at"]


admin.site.register(models.ExpenseCategory)
admin.site.register(models.Expense, ExpenseAdmin)
