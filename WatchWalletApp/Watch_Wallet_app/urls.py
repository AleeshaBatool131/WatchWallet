from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/edit/<int:pk>/', views.transaction_edit, name='transaction_edit'),
    path('transactions/delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.budget_add, name='budget_add'),
    path('budgets/edit/<int:pk>/', views.budget_edit, name='budget_edit'),
    path('budgets/delete/<int:pk>/', views.budget_delete, name='budget_delete'),
    
    # Recurring Transactions
    path('recurring/', views.recurring_list, name='recurring_list'),
    path('recurring/add/', views.recurring_add, name='recurring_add'),
    path('recurring/edit/<int:pk>/', views.recurring_edit, name='recurring_edit'),
    path('recurring/delete/<int:pk>/', views.recurring_delete, name='recurring_delete'),
    path('recurring/process/', views.process_recurring, name='process_recurring'),
    
    # Savings Goals
    path('goals/', views.savings_goal_list, name='savings_goal_list'),
    path('goals/add/', views.savings_goal_add, name='savings_goal_add'),
    path('goals/edit/<int:pk>/', views.savings_goal_edit, name='savings_goal_edit'),
    path('goals/delete/<int:pk>/', views.savings_goal_delete, name='savings_goal_delete'),
    path('goals/add-contribution/<int:pk>/', views.savings_goal_contribute, name='savings_goal_contribute'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    path('reports/export-csv/', views.export_csv, name='export_csv'),
]