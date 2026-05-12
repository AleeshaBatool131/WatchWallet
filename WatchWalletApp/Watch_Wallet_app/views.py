from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, TransactionForm, CategoryForm, BudgetForm, RecurringTransactionForm, SavingsGoalForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category, Budget, RecurringTransaction, SavingsGoal
from django.db.models import Sum
from datetime import date, timedelta, datetime
from django.utils import timezone



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'Watch_Wallet_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(None)

            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    
    else:
        form = LoginForm()
        
    return render(request, 'Watch_Wallet_app/login.html',{'form': form})

@login_required
def dashboard(request):
    today = date.today()
    current_month = today.month
    current_year = today.year

    transactions = Transaction.objects.filter(
        user = request.user,
        date__month = current_month,
        date__year = current_year
        )
    category_id = request.GET.get('category')
    start_date= request.GET.get('start_date')
    end_date= request.GET.get('end_date')
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    total_income = transactions.filter(transaction_type = 'income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type = 'expense').aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transactions': transactions
    }
    # expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    return render(request, 'Watch_Wallet_app/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def get_categories(request):
    """AJAX view to get categories based on transaction type"""
    transaction_type = request.GET.get('type')
    if transaction_type:
        categories = Category.objects.filter(user=request.user, type=transaction_type)
        data = {'categories': list(categories.values('id', 'name'))}
    return JsonResponse(data)

# ============ Transaction CRUD Views ============

@login_required
def transaction_list(request):
    """List all transactions with filtering"""
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category').order_by('-date')
    
    # Apply filters
    category_id = request.GET.get('category')
    trans_type = request.GET.get('type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if trans_type:
        transactions = transactions.filter(transaction_type=trans_type)
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    
    # Calculate totals
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
    }
    return render(request, 'Watch_Wallet_app/transaction_list.html', context)

@login_required
def transaction_add(request):
    """Add a new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            if category == '__add_new__':
                # Store form data in session and redirect to add category
                request.session['pending_transaction_data'] = {
                    'transaction_type': form.cleaned_data.get('transaction_type'),
                    'amount': str(form.cleaned_data.get('amount')),
                    'date': str(form.cleaned_data.get('date')),
                    'description': form.cleaned_data.get('description'),
                }
                messages.info(request, "Please add a new category first.")
                return redirect('category_add')
            else:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                messages.success(request, "Transaction added successfully!")
                return redirect('transaction_list')
    else:
        # Check if we have pending transaction data from category creation
        pending_data = request.session.pop('pending_transaction_data', None)
        if pending_data:
            form = TransactionForm(user=request.user, transaction_type=pending_data.get('transaction_type'))
            form.initial = pending_data
        else:
            form = TransactionForm(user=request.user)
    
    return render(request, 'Watch_Wallet_app/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

@login_required
def transaction_edit(request, pk):
    """Edit an existing transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            if category == '__add_new__':
                # Store form data in session and redirect to add category
                request.session['pending_transaction_data'] = {
                    'transaction_type': form.cleaned_data.get('transaction_type'),
                    'amount': str(form.cleaned_data.get('amount')),
                    'date': str(form.cleaned_data.get('date')),
                    'description': form.cleaned_data.get('description'),
                }
                messages.info(request, "Please add a new category first.")
                return redirect('category_add')
            else:
                form.save()
                messages.success(request, "Transaction updated successfully!")
                return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user, transaction_type=transaction.transaction_type)
    
    return render(request, 'Watch_Wallet_app/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})

@login_required
def transaction_delete(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect('transaction_list')
    
    return render(request, 'Watch_Wallet_app/transaction_confirm_delete.html', {'transaction': transaction})

# ============ Category Views ============

@login_required
def category_list(request):
    """List all categories"""
    income_categories = Category.objects.filter(user=request.user, type='income').order_by('name')
    expense_categories = Category.objects.filter(user=request.user, type='expense').order_by('name')
    return render(request, 'Watch_Wallet_app/category_list.html', {
        'income_categories': income_categories,
        'expense_categories': expense_categories
    })

@login_required
def category_add(request):
    """Add a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category added successfully!")
            
            # Check where to redirect
            return_to = request.GET.get('return_to', 'category_list')
            pending_data = request.session.get('pending_transaction_data')
            
            if pending_data:
                # Clear the pending data and redirect back to transaction add
                del request.session['pending_transaction_data']
                return redirect('transaction_add')
            elif return_to == 'transaction_add':
                return redirect('transaction_add')
            else:
                return redirect('category_list')
    else:
        # Pre-fill the type from query parameter or session data
        transaction_type = request.GET.get('type')
        pending_data = request.session.get('pending_transaction_data')
        
        if transaction_type:
            form = CategoryForm(initial={'type': transaction_type})
        elif pending_data:
            form = CategoryForm(initial={'type': pending_data.get('transaction_type')})
        else:
            form = CategoryForm()
    
    return render(request, 'Watch_Wallet_app/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_edit(request, pk):
    """Edit a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'Watch_Wallet_app/category_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect('category_list')
    
    return render(request, 'Watch_Wallet_app/category_confirm_delete.html', {'object': category, 'object_name': 'category'})

# ============ Budget Views ============

@login_required
def budget_list(request):
    """List all budgets"""
    budgets = Budget.objects.filter(user=request.user).select_related('category').order_by('-year', '-month')
    
    # Calculate spending vs budget
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    budget_data = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__month=budget.month,
            date__year=budget.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount_limit - spent,
            'percent_used': (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
        })
    
    return render(request, 'Watch_Wallet_app/budget_list.html', {'budget_data': budget_data})

@login_required
def budget_add(request):
    """Add a new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget added successfully!")
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'Watch_Wallet_app/budget_form.html', {'form': form, 'title': 'Add Budget'})

@login_required
def budget_edit(request, pk):
    """Edit a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully!")
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    return render(request, 'Watch_Wallet_app/budget_form.html', {'form': form, 'title': 'Edit Budget'})

@login_required
def budget_delete(request, pk):
    """Delete a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget deleted successfully!")
        return redirect('budget_list')
    
    return render(request, 'Watch_Wallet_app/budget_confirm_delete.html', {'object': budget, 'object_name': 'budget'})

# ============ Recurring Transaction Views ============

@login_required
def recurring_list(request):
    """List all recurring transactions"""
    recurrings = RecurringTransaction.objects.filter(user=request.user).order_by('-next_run_date')
    return render(request, 'Watch_Wallet_app/recurring_list.html', {'recurrings': recurrings})

@login_required
def recurring_add(request):
    """Add a new recurring transaction"""
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.save()
            messages.success(request, "Recurring transaction added successfully!")
            return redirect('recurring_list')
    else:
        form = RecurringTransactionForm(user=request.user)
    
    return render(request, 'Watch_Wallet_app/recurring_form.html', {'form': form, 'title': 'Add Recurring Transaction'})

@login_required
def recurring_edit(request, pk):
    """Edit a recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=recurring, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurring transaction updated successfully!")
            return redirect('recurring_list')
    else:
        form = RecurringTransactionForm(instance=recurring, user=request.user)
    
    return render(request, 'Watch_Wallet_app/recurring_form.html', {'form': form, 'title': 'Edit Recurring Transaction'})

@login_required
def recurring_delete(request, pk):
    """Delete a recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        recurring.delete()
        messages.success(request, "Recurring transaction deleted successfully!")
        return redirect('recurring_list')
    
    return render(request, 'Watch_Wallet_app/budget_confirm_delete.html', {'object': recurring, 'object_name': 'recurring transaction'})

@login_required
def process_recurring(request):
    """Process due recurring transactions"""
    from .models import RecurringTransaction
    
    today = date.today()
    due_recurrings = RecurringTransaction.objects.filter(
        user=request.user,
        is_active=True,
        next_run_date__lte=today
    )
    
    processed_count = 0
    for recurring in due_recurrings:
        # Create transaction
        Transaction.objects.create(
            user=recurring.user,
            category=recurring.category,
            amount=recurring.amount,
            transaction_type=recurring.transaction_type,
            date=today,
            description=f"Recurring: {recurring.description or recurring.category.name}"
        )
        
        # Update next run date
        if recurring.frequency == 'daily':
            recurring.next_run_date = today + timedelta(days=1)
        elif recurring.frequency == 'weekly':
            recurring.next_run_date = today + timedelta(weeks=1)
        elif recurring.frequency == 'biweekly':
            recurring.next_run_date = today + timedelta(weeks=2)
        elif recurring.frequency == 'monthly':
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year if today.month < 12 else today.year + 1
            try:
                recurring.next_run_date = date(next_year, next_month, today.day)
            except:
                recurring.next_run_date = date(next_year, next_month, 28)
        elif recurring.frequency == 'quarterly':
            next_month = today.month + 3
            next_year = today.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            try:
                recurring.next_run_date = date(next_year, next_month, today.day)
            except:
                recurring.next_run_date = date(next_year, next_month, 28)
        elif recurring.frequency == 'yearly':
            recurring.next_run_date = date(today.year + 1, today.month, today.day)
        
        # Check if should be deactivated
        if recurring.end_date and recurring.next_run_date > recurring.end_date:
            recurring.is_active = False
        
        recurring.save()
        processed_count += 1
    
    if processed_count > 0:
        messages.success(request, f"Processed {processed_count} recurring transaction(s)!")
    else:
        messages.info(request, "No recurring transactions due today.")
    
    return redirect('dashboard')

# ============ Savings Goal Views ============

@login_required
def savings_goal_list(request):
    """List all savings goals"""
    goals = SavingsGoal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Watch_Wallet_app/savings_goal_list.html', {'goals': goals})

@login_required
def savings_goal_add(request):
    """Add a new savings goal"""
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings goal added successfully!")
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm()
    
    return render(request, 'Watch_Wallet_app/savings_goal_form.html', {'form': form, 'title': 'Add Savings Goal'})

@login_required
def savings_goal_edit(request, pk):
    """Edit a savings goal"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Savings goal updated successfully!")
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm(instance=goal)
    
    return render(request, 'Watch_Wallet_app/savings_goal_form.html', {'form': form, 'title': 'Edit Savings Goal'})

@login_required
def savings_goal_delete(request, pk):
    """Delete a savings goal"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Savings goal deleted successfully!")
        return redirect('savings_goal_list')
    
    return render(request, 'Watch_Wallet_app/budget_confirm_delete.html', {'object': goal, 'object_name': 'savings goal'})

@login_required
def savings_goal_contribute(request, pk):
    """Add contribution to savings goal"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('contribution_amount')
        try:
            amount = float(amount)
            goal.current_amount += amount
            if goal.current_amount >= goal.target_amount:
                goal.status = 'completed'
            goal.save()
            messages.success(request, f"Added ${amount:.2f} to your savings goal!")
        except ValueError:
            messages.error(request, "Invalid amount.")
    
    return redirect('savings_goal_list')

# ============ Reports Views ============

@login_required
def reports_view(request):
    """Financial reports and analytics with detailed insights"""
    from django.db.models import Count, Avg, Sum
    from datetime import datetime, timedelta
    
    # Get date range
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not start_date_str:
        start_date = date(date.today().year, 1, 1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = date(date.today().year, 1, 1)
    
    if not end_date_str:
        end_date = date.today()
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = date.today()
    
    # Ensure start_date is not after end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Get transactions in date range
    transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).select_related('category')
    
    # Calculate totals
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Category breakdown - Income
    income_by_category = transactions.filter(
        transaction_type='income'
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Category breakdown - Expense
    expense_by_category = transactions.filter(
        transaction_type='expense'
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Top 5 spending categories
    top_expense_categories = list(expense_by_category[:5])
    top_income_categories = list(income_by_category[:5])
    
    # Monthly breakdown with aggregation
    monthly_income = transactions.filter(
        transaction_type='income'
    ).values('date__year', 'date__month').annotate(
        total=Sum('amount')
    ).order_by('date__year', 'date__month')
    
    monthly_expense = transactions.filter(
        transaction_type='expense'
    ).values('date__year', 'date__month').annotate(
        total=Sum('amount')
    ).order_by('date__year', 'date__month')
    
    # Calculate daily averages
    days_in_range = (end_date - start_date).days + 1
    avg_daily_income = total_income / days_in_range if days_in_range > 0 else 0
    avg_daily_expense = total_expense / days_in_range if days_in_range > 0 else 0
    
    # Transaction count
    transaction_count = transactions.count()
    income_count = transactions.filter(transaction_type='income').count()
    expense_count = transactions.filter(transaction_type='expense').count()
    
    # Budget utilization
    budgets = Budget.objects.filter(
        user=request.user,
        year__gte=start_date.year,
        month__gte=start_date.month if start_date.year == end_date.year else 1,
        year__lte=end_date.year,
        month__lte=end_date.month if start_date.year == end_date.year else 12
    )
    
    budget_data = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__month=budget.month,
            date__year=budget.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        budget_data.append({
            'category': budget.category.name if budget.category else 'Overall',
            'budget': budget.amount_limit,
            'spent': spent,
            'remaining': budget.amount_limit - spent,
            'percent_used': round((spent / budget.amount_limit * 100), 1) if budget.amount_limit > 0 else 0
        })
    
    # Savings rate
    savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
    
    # Recent transactions for context
    recent_transactions = transactions.order_by('-date')[:10]
    
    # Additional statistics
    # Largest transactions
    largest_income = transactions.filter(transaction_type='income').order_by('-amount').first()
    largest_expense = transactions.filter(transaction_type='expense').order_by('-amount').first()
    
    # Average transaction amounts
    avg_income_amount = transactions.filter(transaction_type='income').aggregate(Avg('amount'))['amount__avg'] or 0
    avg_expense_amount = transactions.filter(transaction_type='expense').aggregate(Avg('amount'))['amount__avg'] or 0
    
    # Weekly breakdown (last 4 weeks)
    today = date.today()
    weekly_data = []
    for i in range(4):
        week_start = today - timedelta(days=today.weekday() + (i * 7))
        week_end = week_start + timedelta(days=6)
        
        week_income = transactions.filter(
            transaction_type='income',
            date__range=[week_start, week_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        week_expense = transactions.filter(
            transaction_type='expense',
            date__range=[week_start, week_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        weekly_data.append({
            'week': f'Week {4-i}',
            'income': week_income,
            'expense': week_expense,
            'start': week_start,
            'end': week_end
        })
    
    # Category spending trends (compare with previous period)
    period_length = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=period_length)
    prev_end = start_date - timedelta(days=1)
    
    prev_transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[prev_start, prev_end]
    )
    
    prev_expense_by_category = prev_transactions.filter(
        transaction_type='expense'
    ).values('category__name').annotate(
        total=Sum('amount')
    )
    
    # Create comparison data
    category_comparison = []
    for curr_cat in expense_by_category:
        prev_cat = next((p for p in prev_expense_by_category if p['category__name'] == curr_cat['category__name']), None)
        prev_amount = prev_cat['total'] if prev_cat else 0
        change = curr_cat['total'] - prev_amount
        change_percent = (change / prev_amount * 100) if prev_amount > 0 else 0
        
        category_comparison.append({
            'category': curr_cat['category__name'],
            'current': curr_cat['total'],
            'previous': prev_amount,
            'change': change,
            'change_percent': round(change_percent, 1)
        })
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'income_by_category': list(income_by_category),
        'expense_by_category': list(expense_by_category),
        'top_expense_categories': top_expense_categories,
        'top_income_categories': top_income_categories,
        'monthly_income': list(monthly_income),
        'monthly_expense': list(monthly_expense),
        'avg_daily_income': round(avg_daily_income, 2),
        'avg_daily_expense': round(avg_daily_expense, 2),
        'transaction_count': transaction_count,
        'income_count': income_count,
        'expense_count': expense_count,
        'budget_data': budget_data,
        'savings_rate': round(savings_rate, 1),
        'recent_transactions': recent_transactions,
        'largest_income': largest_income,
        'largest_expense': largest_expense,
        'avg_income_amount': round(avg_income_amount, 2),
        'avg_expense_amount': round(avg_expense_amount, 2),
        'weekly_data': weekly_data,
        'category_comparison': category_comparison,
    }
    
    return render(request, 'Watch_Wallet_app/reports.html', context)

@login_required
def export_csv(request):
    """Export transactions to CSV"""
    import csv
    from django.http import HttpResponse
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    transactions = Transaction.objects.filter(user=request.user).select_related('category')
    
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])
    
    for t in transactions.order_by('-date'):
        writer.writerow([t.date, t.transaction_type, t.category.name, t.amount, t.description or ''])
    
    return response

@login_required
def budget_report(request):
    """Detailed budget analysis report"""
    from django.db.models import Sum
    
    # Get current month/year or from parameters
    current_month = int(request.GET.get('month', date.today().month))
    current_year = int(request.GET.get('year', date.today().year))
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')
    
    budget_analysis = []
    total_budgeted = 0.0
    total_spent = 0.0
    
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__month=current_month,
            date__year=current_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        spent = float(spent)
        budget_limit = float(budget.amount_limit)
        
        total_budgeted += budget_limit
        total_spent += spent
        
        budget_analysis.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget_limit - spent,
            'percent_used': (spent / budget_limit * 100) if budget_limit > 0 else 0,
            'status': 'over_budget' if spent > budget_limit else 'on_track' if spent > budget_limit * 0.8 else 'good'
        })
    
    # Overall budget status
    overall_budget = Budget.objects.filter(
        user=request.user,
        category__isnull=True,
        month=current_month,
        year=current_year
    ).first()
    
    if overall_budget:
        overall_spent = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__month=current_month,
            date__year=current_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        overall_spent = float(overall_spent)
        overall_budget_limit = float(overall_budget.amount_limit)
        
        budget_analysis.insert(0, {
            'budget': overall_budget,
            'spent': overall_spent,
            'remaining': overall_budget_limit - overall_spent,
            'percent_used': (overall_spent / overall_budget_limit * 100) if overall_budget_limit > 0 else 0,
            'status': 'over_budget' if overall_spent > overall_budget_limit else 'on_track' if overall_spent > overall_budget_limit * 0.8 else 'good'
        })
    
    context = {
        'budget_analysis': budget_analysis,
        'current_month': current_month,
        'current_year': current_year,
        'total_budgeted': total_budgeted,
        'total_spent': total_spent,
        'month_name': date(current_year, current_month, 1).strftime('%B %Y')
    }
    
    return render(request, 'Watch_Wallet_app/budget_report.html', context)

@login_required
def category_report(request):
    """Detailed category analysis report"""
    from django.db.models import Sum, Count, Avg

    # Get date range
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str:
        start_date = date(date.today().year, date.today().month, 1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = date(date.today().year, date.today().month, 1)

    if not end_date_str:
        end_date = date.today()
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = date.today()

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Category analysis for expenses
    expense_analysis = list(Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__range=[start_date, end_date]
    ).values('category__name').annotate(
        total_amount=Sum('amount'),
        transaction_count=Count('id'),
        avg_amount=Avg('amount')
    ).order_by('-total_amount'))

    # Category analysis for income
    income_analysis = list(Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__range=[start_date, end_date]
    ).values('category__name').annotate(
        total_amount=Sum('amount'),
        transaction_count=Count('id'),
        avg_amount=Avg('amount')
    ).order_by('-total_amount'))

    expense_total = sum(item['total_amount'] for item in expense_analysis)
    income_total = sum(item['total_amount'] for item in income_analysis)

    for item in expense_analysis:
        item['percent_of_total'] = round(item['total_amount'] / expense_total * 100, 1) if expense_total else 0
    for item in income_analysis:
        item['percent_of_total'] = round(item['total_amount'] / income_total * 100, 1) if income_total else 0

    top_categories = [cat['category__name'] for cat in expense_analysis[:5]]
    trend_sets = []

    for category_name in top_categories:
        monthly_data = Transaction.objects.filter(
            user=request.user,
            category__name=category_name,
            transaction_type='expense',
            date__range=[start_date, end_date]
        ).values('date__year', 'date__month').annotate(
            total=Sum('amount')
        ).order_by('date__year', 'date__month')

        months = [f"{item['date__year']}-{str(item['date__month']).zfill(2)}" for item in monthly_data]
        totals = [item['total'] for item in monthly_data]

        trend_sets.append({
            'category': category_name,
            'months': months,
            'totals': totals
        })

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'expense_analysis': expense_analysis,
        'income_analysis': income_analysis,
        'expense_total': expense_total,
        'income_total': income_total,
        'expense_labels': [item['category__name'] for item in expense_analysis[:8]],
        'expense_totals': [item['total_amount'] for item in expense_analysis[:8]],
        'trend_sets': trend_sets,
        'top_categories': top_categories,
    }

    return render(request, 'Watch_Wallet_app/category_report.html', context)

@login_required
def trends_report(request):
    """Financial trends and forecasting report"""
    from django.db.models import Sum
    from datetime import timedelta
    
    # Get last 12 months of data
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    # Monthly income/expense trends
    monthly_data = []
    for i in range(12):
        month_start = start_date + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        income = float(income)
        
        expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        expense = float(expense)
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': income,
            'expense': expense,
            'balance': income - expense
        })
    
    # Calculate trends
    if len(monthly_data) >= 3:
        recent_months = monthly_data[-3:]
        income_trend = sum(m['income'] for m in recent_months) / 3
        expense_trend = sum(m['expense'] for m in recent_months) / 3
        
        # Simple linear regression for forecasting
        x = list(range(len(monthly_data)))
        y_income = [m['income'] for m in monthly_data]
        y_expense = [m['expense'] for m in monthly_data]
        
        # Calculate slopes (simplified)
        income_slope = (y_income[-1] - y_income[0]) / len(y_income) if len(y_income) > 1 else 0
        expense_slope = (y_expense[-1] - y_expense[0]) / len(y_expense) if len(y_expense) > 1 else 0
    else:
        income_trend = expense_trend = income_slope = expense_slope = 0
    
    context = {
        'monthly_data': monthly_data,
        'income_trend': round(income_trend, 2),
        'expense_trend': round(expense_trend, 2),
        'income_slope': round(income_slope, 2),
        'expense_slope': round(expense_slope, 2),
        'forecast_income': round(income_trend + income_slope, 2),
        'forecast_expense': round(expense_trend + expense_slope, 2),
        'forecast_balance': round((income_trend + income_slope) - (expense_trend + expense_slope), 2),
        'cash_flow_diff': round(abs(income_trend - expense_trend), 2),
        'cash_flow_positive': income_trend >= expense_trend,
        'forecast_period': 3  # months
    }
    
    return render(request, 'Watch_Wallet_app/trends_report.html', context)