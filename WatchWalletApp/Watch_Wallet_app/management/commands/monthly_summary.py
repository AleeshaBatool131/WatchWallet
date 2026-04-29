"""
Management command to generate monthly financial summary reports.
Can be scheduled to run at the end of each month.

Usage:
    python manage.py monthly_summary
    python manage.py monthly_summary --user-id=1 --month=3 --year=2026
    python manage.py monthly_summary --email  # Send via email
"""
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import date, timedelta
from calendar import monthrange
from Watch_Wallet_app.models import Transaction, Budget


class Command(BaseCommand):
    help = 'Generate monthly financial summary report'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate summary for a specific user',
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Month number (1-12). Defaults to previous month.',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year. Defaults to current year.',
        )
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send summary via email',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Generate summary for all users',
        )
    
    def handle(self, *args, **options):
        today = date.today()
        
        # Determine month and year
        month = options.get('month')
        year = options.get('year')
        
        if not month:
            # Default to previous month
            if today.month == 1:
                month = 12
                year = today.year - 1
            else:
                month = today.month - 1
                year = today.year
        else:
            year = year or today.year
        
        if options.get('all_users'):
            users = User.objects.filter(is_active=True)
        elif options.get('user_id'):
            users = User.objects.filter(id=options.get('user_id'))
        else:
            self.stdout.write(self.style.ERROR('Please specify --user-id or --all-users'))
            return
        
        for user in users:
            self._generate_summary(user, month, year, options)
    
    def _generate_summary(self, user, month, year, options):
        """Generate summary for a single user"""
        self.stdout.write(f'\n=== Monthly Summary for {user.username} - {month}/{year} ===')
        
        # Get transactions for the month
        transactions = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        )
        
        # Calculate totals
        total_income = transactions.filter(
            transaction_type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_expense = transactions.filter(
            transaction_type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        balance = total_income - total_expense
        savings_rate = (balance / total_income * 100) if total_income > 0 else 0
        
        # Transaction count
        income_count = transactions.filter(transaction_type='income').count()
        expense_count = transactions.filter(transaction_type='expense').count()
        
        # Top categories
        top_expenses = transactions.filter(
            transaction_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        top_income = transactions.filter(
            transaction_type='income'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        # Budget status
        budgets = Budget.objects.filter(user=user, month=month, year=year)
        budget_status = []
        
        for budget in budgets:
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_type='expense',
                date__month=month,
                date__year=year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            percent_used = (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
            status = '✅' if percent_used < 80 else '⚠️' if percent_used < 100 else '❌'
            
            budget_status.append({
                'category': budget.category.name if budget.category else 'Overall',
                'budget': budget.amount_limit,
                'spent': spent,
                'remaining': budget.amount_limit - spent,
                'percent': round(percent_used, 1),
                'status': status
            })
        
        # Print summary
        self.stdout.write(f'Income: ${total_income:,.2f} ({income_count} transactions)')
        self.stdout.write(f'Expenses: ${total_expense:,.2f} ({expense_count} transactions)')
        self.stdout.write(f'Balance: ${balance:,.2f}')
        self.stdout.write(f'Savings Rate: {savings_rate:.1f}%')
        
        if top_expenses:
            self.stdout.write('\nTop Expense Categories:')
            for item in top_expenses:
                self.stdout.write(f'  - {item["category__name"]}: ${item["total"]:,.2f}')
        
        if top_income:
            self.stdout.write('\nTop Income Categories:')
            for item in top_income:
                self.stdout.write(f'  - {item["category__name"]}: ${item["total"]:,.2f}')
        
        if budget_status:
            self.stdout.write('\nBudget Status:')
            for b in budget_status:
                self.stdout.write(
                    f'  {b["status"]} {b["category"]}: ${b["spent"]:,.2f} / '
                    f'${b["budget"]:,.2f} ({b["percent"]}%)'
                )
        
        # Email option
        if options.get('email'):
            self._send_email(user, month, year, total_income, total_expense, balance, savings_rate)
    
    def _send_email(self, user, month, year, income, expense, balance, savings_rate):
        """Send summary via email"""
        # This is a placeholder - implement with Django's email backend
        self.stdout.write(self.style.SUCCESS(f'  [Email] Would send summary to {user.email}'))