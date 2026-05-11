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
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
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
            'Investments',
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
            ('income', income_cat_objects[0], Decimal('5000.00'), today - timedelta(days=0), 'Monthly Salary'),
            ('income', income_cat_objects[1], Decimal('800.00'), today - timedelta(days=3), 'Freelance Project'),
            ('income', income_cat_objects[2], Decimal('150.00'), today - timedelta(days=5), 'Stock Dividends'),
            
            # Expense transactions
            ('expense', expense_cat_objects[9], Decimal('1500.00'), today - timedelta(days=1), 'Monthly Rent'),
            ('expense', expense_cat_objects[0], Decimal('120.50'), today - timedelta(days=2), 'Weekly Groceries'),
            ('expense', expense_cat_objects[3], Decimal('45.00'), today - timedelta(days=4), 'Gas'),
            ('expense', expense_cat_objects[1], Decimal('85.00'), today - timedelta(days=5), 'Electricity Bill'),
            ('expense', expense_cat_objects[4], Decimal('65.99'), today - timedelta(days=6), 'Restaurant Dinner'),
            ('expense', expense_cat_objects[5], Decimal('200.00'), today - timedelta(days=7), 'New Shoes'),
            ('expense', expense_cat_objects[6], Decimal('50.00'), today - timedelta(days=8), 'Doctor Visit'),
            ('expense', expense_cat_objects[2], Decimal('35.00'), today - timedelta(days=9), 'Movie Tickets'),
            ('expense', expense_cat_objects[0], Decimal('95.30'), today - timedelta(days=10), 'Groceries'),
            ('expense', expense_cat_objects[7], Decimal('100.00'), today - timedelta(days=11), 'Online Course'),
            ('expense', expense_cat_objects[8], Decimal('200.00'), today - timedelta(days=12), 'Health Insurance'),
            ('expense', expense_cat_objects[1], Decimal('60.00'), today - timedelta(days=13), 'Internet Bill'),
        ]
        
        for trans_type, category, amount, trans_date, description in transactions_data:
            trans, created = Transaction.objects.get_or_create(
                user=user,
                category=category,
                amount=amount,
                transaction_type=trans_type,
                date=trans_date,
                description=description
            )
            if created:
                self.stdout.write(f'Created transaction: {trans_type} - {amount} ({category.name})')

        # Sample Budgets
        budgets_data = [
            (expense_cat_objects[0], today.year, today.month, Decimal('300.00')),  # Groceries
            (expense_cat_objects[4], today.year, today.month, Decimal('150.00')),  # Dining Out
            (expense_cat_objects[5], today.year, today.month, Decimal('200.00')),  # Shopping
            (expense_cat_objects[2], today.year, today.month, Decimal('100.00')),  # Entertainment
            (expense_cat_objects[9], today.year, today.month, Decimal('1500.00')), # Rent
        ]
        
        for category, year, month, amount_limit in budgets_data:
            budget, created = Budget.objects.get_or_create(
                user=user,
                category=category,
                year=year,
                month=month,
                amount_limit=amount_limit
            )
            if created:
                self.stdout.write(f'Created budget: {category.name} - ${amount_limit}')

        # Sample Recurring Transactions
        next_run = today + timedelta(days=15)
        
        recurring_data = [
            (income_cat_objects[0], Decimal('5000.00'), 'income', 'monthly', today, None, next_run, 'Monthly Salary'),
            (expense_cat_objects[9], Decimal('1500.00'), 'expense', 'monthly', today, None, next_run, 'Monthly Rent'),
            (expense_cat_objects[1], Decimal('85.00'), 'expense', 'monthly', today, None, next_run + timedelta(days=5), 'Electricity Bill'),
            (expense_cat_objects[8], Decimal('200.00'), 'expense', 'monthly', today, None, next_run + timedelta(days=10), 'Health Insurance'),
        ]
        
        for category, amount, trans_type, frequency, start_date, end_date, next_run_date, description in recurring_data:
            recurring, created = RecurringTransaction.objects.get_or_create(
                user=user,
                category=category,
                amount=amount,
                transaction_type=trans_type,
                frequency=frequency,
                start_date=start_date,
                next_run_date=next_run_date,
                description=description,
                defaults={'end_date': end_date, 'is_active': True}
            )
            if created:
                self.stdout.write(f'Created recurring: {description} - ${amount} ({frequency})')

        # Sample Savings Goals
        savings_goals_data = [
            ('Vacation', Decimal('3000.00'), Decimal('1200.00'), today + timedelta(days=180)),
            ('Emergency Fund', Decimal('10000.00'), Decimal('5000.00'), None),
            ('New Car', Decimal('25000.00'), Decimal('8500.00'), today + timedelta(days=365)),
            ('Home Renovation', Decimal('15000.00'), Decimal('3000.00'), today + timedelta(days=270)),
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
            if created:
                self.stdout.write(f'Created savings goal: {name} - ${target}')

        self.stdout.write(self.style.SUCCESS('Sample data population complete!'))
        self.stdout.write(self.style.WARNING(f'\nTest User Credentials:\nUsername: testuser\nPassword: testpass123'))
