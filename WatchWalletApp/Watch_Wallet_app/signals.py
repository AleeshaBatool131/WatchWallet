from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category, Transaction, RecurringTransaction
from datetime import date, timedelta

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

@receiver(post_save, sender=RecurringTransaction)
def process_recurring_on_create(sender, instance, created, **kwargs):
    """Automatically process recurring transaction when it's created if it's due today"""
    if created and instance.is_active:
        today = date.today()
        if instance.next_run_date <= today:
            # Create the first transaction immediately
            Transaction.objects.create(
                user=instance.user,
                category=instance.category,
                amount=instance.amount,
                transaction_type=instance.transaction_type,
                date=today,
                description=f"Recurring: {instance.description or instance.category.name}"
            )
            # Calculate next run date
            instance.next_run_date = calculate_next_run_date(instance, today)
            instance.save()

def calculate_next_run_date(recurring, from_date):
    """Calculate the next run date based on frequency"""
    if recurring.frequency == 'daily':
        return from_date + timedelta(days=1)
    elif recurring.frequency == 'weekly':
        return from_date + timedelta(weeks=1)
    elif recurring.frequency == 'biweekly':
        return from_date + timedelta(weeks=2)
    elif recurring.frequency == 'monthly':
        return add_months(from_date, 1)
    elif recurring.frequency == 'quarterly':
        return add_months(from_date, 3)
    elif recurring.frequency == 'yearly':
        return add_months(from_date, 12)
    return from_date + timedelta(days=30)

def add_months(d, months):
    """Add months to a date, handling edge cases like end of month"""
    import calendar
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(d.day, max_day)
    return date(year, month, day)