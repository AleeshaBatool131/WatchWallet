from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Watch_Wallet_app.models import Category, Transaction, Budget, RecurringTransaction, SavingsGoal
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='ali',
            defaults={
                'email': 'ali@gmail.com',
                'first_name': 'Ali',
                'last_name': 'Mehdi'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {user.username} already exists'))

        # Income Categories
        income_categories = [
            'Salary',
            'Freelance Work',
            'Investment',
            'Bonus',
            'Gifts',
        ]
        
        income_cat_objects = []
        for cat_name in income_categories:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=cat_name,
                type='income'
            )
            income_cat_objects.append(cat)
            if created:
                self.stdout.write(f'Created income category: {cat_name}')

        # Expense Categories
        expense_categories = [
            'Groceries',
            'Utilities',
            'Entertainment',
            'Transportation',
            'Dining Out',
            'Shopping',
            'Healthcare',
            'Education',
            'Insurance',
            'Rent',
        ]
        
        expense_cat_objects = []
        for cat_name in expense_categories:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=cat_name,
                type='expense'
            )
            expense_cat_objects.append(cat)
            if created:
                self.stdout.write(f'Created expense category: {cat_name}')

        # Sample Transactions
        today = date.today()
        
        transactions_data = [
            # Income transactions
            ('income', income_cat_objects[0], Decimal('150000.00'), today - timedelta(days=0), 'Monthly Salary'),
            ('income', income_cat_objects[1], Decimal('20000.00'), today - timedelta(days=3), 'Freelance Project'),
            ('income', income_cat_objects[2], Decimal('5000.00'), today - timedelta(days=5), 'Stock Dividends'),
            ('income', income_cat_objects[3], Decimal('10000.00'), today - timedelta(days=7), 'Year-end Bonus'),
            ('income', income_cat_objects[4], Decimal('3000.00'), today - timedelta(days=9), 'Family Gift'),
            
            # Expense transactions
            ('expense', expense_cat_objects[9], Decimal('50000.00'), today - timedelta(days=1), 'Monthly Rent'),
            ('expense', expense_cat_objects[0], Decimal('2500.00'), today - timedelta(days=2), 'Weekly Groceries'),
            ('expense', expense_cat_objects[3], Decimal('1200.00'), today - timedelta(days=4), 'Fuel'),
            ('expense', expense_cat_objects[1], Decimal('4500.00'), today - timedelta(days=5), 'Electricity Bill'),
            ('expense', expense_cat_objects[4], Decimal('3200.00'), today - timedelta(days=6), 'Dinner Out'),
            ('expense', expense_cat_objects[5], Decimal('9000.00'), today - timedelta(days=7), 'New Clothes'),
            ('expense', expense_cat_objects[6], Decimal('3500.00'), today - timedelta(days=8), 'Doctor Visit'),
            ('expense', expense_cat_objects[2], Decimal('1800.00'), today - timedelta(days=9), 'Movie Tickets'),
            ('expense', expense_cat_objects[0], Decimal('2400.00'), today - timedelta(days=10), 'Groceries'),
            ('expense', expense_cat_objects[7], Decimal('5500.00'), today - timedelta(days=11), 'Online Course'),
            ('expense', expense_cat_objects[8], Decimal('7000.00'), today - timedelta(days=12), 'Health Insurance'),
            ('expense', expense_cat_objects[1], Decimal('4000.00'), today - timedelta(days=13), 'Internet Bill'),
        ]
        
        for trans_type, category, amount, trans_date, description in transactions_data:
            trans, created = Transaction.objects.get_or_create(
                user=user,
                category=category,
                transaction_type=trans_type,
                date=trans_date,
                description=description,
                defaults={'amount': amount}
            )
            if not created and trans.amount != amount:
                trans.amount = amount
                trans.save()
            if created:
                self.stdout.write(f'Created transaction: {trans_type} - {amount} ({category.name})')
            elif trans.amount == amount:
                self.stdout.write(f'Updated transaction amount: {trans_type} - {amount} ({category.name})')

        # Sample Budgets
        budgets_data = [
            (expense_cat_objects[0], today.year, today.month, Decimal('22000.00')),  # Groceries
            (expense_cat_objects[4], today.year, today.month, Decimal('8000.00')),   # Dining Out
            (expense_cat_objects[5], today.year, today.month, Decimal('15000.00')),  # Shopping
            (expense_cat_objects[2], today.year, today.month, Decimal('6000.00')),   # Entertainment
            (expense_cat_objects[9], today.year, today.month, Decimal('50000.00')),  # Rent
        ]
        
        for category, year, month, amount_limit in budgets_data:
            budget, created = Budget.objects.get_or_create(
                user=user,
                category=category,
                year=year,
                month=month,
                defaults={'amount_limit': amount_limit}
            )
            if not created and budget.amount_limit != amount_limit:
                budget.amount_limit = amount_limit
                budget.save()
            if created:
                self.stdout.write(f'Created budget: {category.name} - PKR {amount_limit}')
            elif budget.amount_limit == amount_limit:
                self.stdout.write(f'Updated budget: {category.name} - PKR {amount_limit}')

        # Sample Recurring Transactions
        next_run = today + timedelta(days=15)
        
        recurring_data = [
            (income_cat_objects[0], Decimal('150000.00'), 'income', 'monthly', today, None, next_run, 'Monthly Salary'),
            (expense_cat_objects[9], Decimal('50000.00'), 'expense', 'monthly', today, None, next_run, 'Monthly Rent'),
            (expense_cat_objects[1], Decimal('4500.00'), 'expense', 'monthly', today, None, next_run + timedelta(days=5), 'Electricity Bill'),
            (expense_cat_objects[8], Decimal('7000.00'), 'expense', 'monthly', today, None, next_run + timedelta(days=10), 'Health Insurance'),
        ]
        
        for category, amount, trans_type, frequency, start_date, end_date, next_run_date, description in recurring_data:
            recurring, created = RecurringTransaction.objects.get_or_create(
                user=user,
                category=category,
                transaction_type=trans_type,
                frequency=frequency,
                description=description,
                defaults={
                    'amount': amount,
                    'start_date': start_date,
                    'next_run_date': next_run_date,
                    'end_date': end_date,
                    'is_active': True
                }
            )
            if not created:
                updated = False
                if recurring.amount != amount:
                    recurring.amount = amount
                    updated = True
                if recurring.start_date != start_date:
                    recurring.start_date = start_date
                    updated = True
                if recurring.next_run_date != next_run_date:
                    recurring.next_run_date = next_run_date
                    updated = True
                if recurring.end_date != end_date:
                    recurring.end_date = end_date
                    updated = True
                if not recurring.is_active:
                    recurring.is_active = True
                    updated = True
                if updated:
                    recurring.save()
            if created:
                self.stdout.write(f'Created recurring: {description} - PKR {amount} ({frequency})')
            elif not created and updated:
                self.stdout.write(f'Updated recurring: {description} - PKR {amount} ({frequency})')

        # Sample Savings Goals
        savings_goals_data = [
            ('Vacation', Decimal('100000.00'), Decimal('35000.00'), today + timedelta(days=180)),
            ('Emergency Fund', Decimal('250000.00'), Decimal('90000.00'), None),
            ('New Car', Decimal('1200000.00'), Decimal('250000.00'), today + timedelta(days=365)),
            ('Home Renovation', Decimal('450000.00'), Decimal('120000.00'), today + timedelta(days=270)),
        ]
        
        for name, target, current, deadline in savings_goals_data:
            goal, created = SavingsGoal.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'target_amount': target,
                    'current_amount': current,
                    'deadline': deadline,
                    'status': 'active'
                }
            )
            if not created:
                updated = False
                if goal.target_amount != target:
                    goal.target_amount = target
                    updated = True
                if goal.current_amount != current:
                    goal.current_amount = current
                    updated = True
                if goal.deadline != deadline:
                    goal.deadline = deadline
                    updated = True
                if goal.status != 'active':
                    goal.status = 'active'
                    updated = True
                if updated:
                    goal.save()
            if created:
                self.stdout.write(f'Created savings goal: {name} - PKR {target}')
            elif not created and updated:
                self.stdout.write(f'Updated savings goal: {name} - PKR {target}')

        self.stdout.write(self.style.SUCCESS('Sample data population complete!'))
        self.stdout.write(self.style.WARNING(f'\nTest User Credentials:\nUsername: ali\nPassword: testpass123'))
