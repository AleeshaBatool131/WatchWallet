from django.contrib.auth.models import User
from Watch_Wallet_app.models import Category, Transaction, Budget, RecurringTransaction, SavingsGoal
from django.db.models import Sum

user = User.objects.get(username='testuser')
print('=== Sample Data Summary ===')
print(f'User: {user.username}')
print(f'Income Categories: {Category.objects.filter(user=user, type="income").count()}')
print(f'Expense Categories: {Category.objects.filter(user=user, type="expense").count()}')
print(f'Transactions: {Transaction.objects.filter(user=user).count()}')
print(f'Budgets: {Budget.objects.filter(user=user).count()}')
print(f'Recurring Transactions: {RecurringTransaction.objects.filter(user=user).count()}')
print(f'Savings Goals: {SavingsGoal.objects.filter(user=user).count()}')

income_total = Transaction.objects.filter(user=user, transaction_type='income').aggregate(Sum('amount'))
expense_total = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(Sum('amount'))

print(f'\nTotal Income: ${income_total["amount__sum"] or 0}')
print(f'Total Expenses: ${expense_total["amount__sum"] or 0}')
print(f'Net Balance: ${(income_total["amount__sum"] or 0) - (expense_total["amount__sum"] or 0)}')
