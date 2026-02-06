from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'Watch_Wallet_app/signup.html',{'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password') #prevent server crash if field is unavailable
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'Watch_Wallet_app/login.html',{
                'error': 'Invalid credentials'})
        
    return render(request, 'Watch_Wallet_app/login.html')

@login_required
def dashboard(request):
    return render(request, 'Watch_Wallet_app/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')
