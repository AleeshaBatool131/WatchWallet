from django.urls import path
from .import views

urlpatterns = [
    path('Watch_Wallet_app/', views.walletApp, name = 'walletApp'),
    ]