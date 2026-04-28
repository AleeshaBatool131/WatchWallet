from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, LoginForm, TransactionForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category, Budget, RecurringTransaction, SavingsGoal
from django.db.models import Sum
from datetime import date, timedelta
from django.utils import timezone



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request,f"Welcome {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'Watch_Wallet_app/signup.html',{'form': form})

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
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added successfully!")
            return redirect('transaction_list')
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
            form.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
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
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'Watch_Wallet_app/category_list.html', {'categories': categories})

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
            return redirect('category_list')
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
    """Financial reports and analytics"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = date(date.today().year, 1, 1)
    else:
        start_date = date.fromisoformat(start_date)
    
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)
    
    # Get transactions in date range
    transactions = Transaction.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).select_related('category')
    
    # Calculate totals
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Category breakdown
    income_by_category = transactions.filter(
        transaction_type='income'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    expense_by_category = transactions.filter(
        transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    # Monthly breakdown
    monthly_data = transactions.extra(
        select={'month': "strftime('%%Y-%%m', date)"}
    ).values('month', 'transaction_type').annotate(total=Sum('amount')).order_by('month')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'income_by_category': list(income_by_category),
        'expense_by_category': list(expense_by_category),
        'monthly_data': list(monthly_data),
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