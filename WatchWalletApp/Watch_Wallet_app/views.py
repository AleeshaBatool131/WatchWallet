from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, ExpenseForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Expense, Transaction
from django.db.models import Sum
from datetime import date



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
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    return render(request, 'Watch_Wallet_app/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
            form = ExpenseForm(user=request.user)
        
    return render(request, 'Watch_Wallet_app/add_expense.html', {'form': form})

@login_required
def expense_list(request):
    expenses = request.user.expenses.select_related('category')
    return render(request, 'Watch_Wallet_app/expense_list.html', {'expenses': expenses})