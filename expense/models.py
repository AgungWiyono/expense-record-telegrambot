from django.db import models


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "expense_category"


class Expense(models.Model):
    title = models.CharField(max_length=64)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    receipt = models.ImageField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "expense"
