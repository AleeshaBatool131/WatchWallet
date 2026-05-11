from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Watch_Wallet_app.models import Category, Transaction, Budget, RecurringTransaction, SavingsGoal
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Verify sample data was created'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='testuser')
            
            income_count = Category.objects.filter(user=user, type='income').count()
            expense_count = Category.objects.filter(user=user, type='expense').count()
            trans_count = Transaction.objects.filter(user=user).count()
            budget_count = Budget.objects.filter(user=user).count()
            recurring_count = RecurringTransaction.objects.filter(user=user).count()
            goals_count = SavingsGoal.objects.filter(user=user).count()
            
            income_total = Transaction.objects.filter(user=user, transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
            expense_total = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
            
            self.stdout.write(self.style.SUCCESS('=== Sample Data Summary ==='))
            self.stdout.write(f'User: {user.username}')
            self.stdout.write(f'Income Categories: {income_count}')
            self.stdout.write(f'Expense Categories: {expense_count}')
            self.stdout.write(f'Transactions: {trans_count}')
            self.stdout.write(f'Budgets: {budget_count}')
            self.stdout.write(f'Recurring Transactions: {recurring_count}')
            self.stdout.write(f'Savings Goals: {goals_count}')
            self.stdout.write('')
            self.stdout.write(f'Total Income: ${income_total}')
            self.stdout.write(f'Total Expenses: ${expense_total}')
            self.stdout.write(f'Net Balance: ${income_total - expense_total}')
            self.stdout.write(self.style.SUCCESS('\nSample data is ready for testing!'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test user not found. Run populate_sample_data first.'))
