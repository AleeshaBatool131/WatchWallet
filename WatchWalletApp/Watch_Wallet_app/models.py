from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank = True
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    date = models.DateField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    
class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name = 'expenses'
    )
    title =  models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    notes = models.TextField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.title} - {self.amount}"
    def save(self, *args, **kwargs):
        """
        Automatically create a corresponding Transaction when an Expense is added.
        """
        super().save(*args, **kwargs)  # save expense first
        from yourapp.models import Transaction
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=self.amount,
            transaction_type='expense',
            date=self.date,
            description=f"Expense: {self.description}" if self.description else "Expense recorded"
        )
    
class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='budgets'
    )
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    amount_limit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        if self.category:
            return f"{self.category} - {self.month}/{self.year}"
        return f"Overall Budget - {self.month}/{self.year}"
