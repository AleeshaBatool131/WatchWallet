from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category, Transaction

DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Entertainment",
    "Health",
    "Others",
    ]
 
@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        for name in DEFAULT_CATEGORIES:
            Category.objects.create(
                user = instance,
                name = name
                )
            
"""@receiver(post_delete, sender = Expense)
def delete_related_transaction(sender, instance, **kwargs):
    Transaction.objects.filter(
        user= instance.user,
        amount = instance.amount, 
        date = instance.expense_date,
        transaction_type = 'expense'
        ).delete()"""