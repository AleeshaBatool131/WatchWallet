from django.db.models import Sum
from .models import Transaction

def calculate_balance(user):
    income = Transaction.objects.filter(
        user = user,
        transaction_type = 'income'
        ).aggregate(total=Sum('amount'))['total'] or 0
    expense = Transaction.objects.filter(
        user = user,
        transaction_type = 'expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    return income-expense