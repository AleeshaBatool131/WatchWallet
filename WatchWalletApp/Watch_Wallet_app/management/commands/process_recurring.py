"""
Management command to process recurring transactions.
Can be run manually or scheduled via cron/systemd.

Usage:
    python manage.py process_recurring
    python manage.py process_recurring --dry-run  # Preview without creating transactions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, timedelta
from Watch_Wallet_app.models import RecurringTransaction, Transaction


class Command(BaseCommand):
    help = 'Process due recurring transactions and create actual transactions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be processed without creating transactions',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Process recurring transactions for a specific user only',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        user_id = options.get('user_id')
        verbose = options.get('verbose', False)
        
        today = date.today()
        
        # Build query for due recurring transactions
        queryset = RecurringTransaction.objects.filter(
            is_active=True,
            next_run_date__lte=today
        )
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        due_transactions = list(queryset.select_related('category', 'user'))
        
        if not due_transactions:
            self.stdout.write(self.style.SUCCESS('No recurring transactions due today.'))
            return
        
        self.stdout.write(f'Found {len(due_transactions)} recurring transaction(s) due.')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE ==='))
        
        processed_count = 0
        errors = []
        
        for recurring in due_transactions:
            try:
                if dry_run:
                    self.stdout.write(
                        f'  [DRY RUN] Would create: {recurring.transaction_type} - '
                        f'{recurring.amount} for {recurring.user.username}'
                    )
                    continue
                
                # Create the actual transaction
                Transaction.objects.create(
                    user=recurring.user,
                    category=recurring.category,
                    amount=recurring.amount,
                    transaction_type=recurring.transaction_type,
                    date=today,
                    description=f"Recurring: {recurring.description or recurring.category.name}"
                )
                
                # Calculate next run date
                next_date = self._calculate_next_run_date(recurring, today)
                
                # Check if should be deactivated
                should_deactivate = False
                if recurring.end_date and next_date > recurring.end_date:
                    should_deactivate = True
                    recurring.is_active = False
                
                # Update next run date
                recurring.next_run_date = next_date
                recurring.save()
                
                processed_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'  Processed: {recurring.description or recurring.category.name} - '
                        f'{recurring.amount} ({recurring.frequency})'
                    )
                    
            except Exception as e:
                errors.append(f'Error processing {recurring.id}: {str(e)}')
                self.stderr.write(f'Error: {e}')
        
        # Summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Dry run complete. Would process {len(due_transactions)} transaction(s).'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully processed {processed_count} recurring transaction(s).'))
        
        if errors:
            self.stdout.write(self.style.ERROR(f'{len(errors)} error(s) occurred.'))
            for error in errors:
                self.stderr.write(f'  - {error}')
    
    def _calculate_next_run_date(self, recurring, today):
        """Calculate the next run date based on frequency"""
        if recurring.frequency == 'daily':
            return today + timedelta(days=1)
        elif recurring.frequency == 'weekly':
            return today + timedelta(weeks=1)
        elif recurring.frequency == 'biweekly':
            return today + timedelta(weeks=2)
        elif recurring.frequency == 'monthly':
            return self._add_months(today, 1)
        elif recurring.frequency == 'quarterly':
            return self._add_months(today, 3)
        elif recurring.frequency == 'yearly':
            return self._add_months(today, 12)
        return today + timedelta(days=30)
    
    def _add_months(self, d, months):
        """Add months to a date, handling edge cases like end of month"""
        year = d.year + (d.month - 1 + months) // 12
        month = (d.month - 1 + months) % 12 + 1
        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28)
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(d.day, max_day)
        return date(year, month, day)