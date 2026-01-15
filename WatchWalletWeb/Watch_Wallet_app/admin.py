from django.contrib import admin
from .models import Category, Expense, Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'user', 'created_at')
    search_fields=('name',)
    list_filter=('user',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display=(
        'title',
        'user',
        'category',
        'amount',
        'expense_date',
        'created_at'
        )
    list_filter=('category','expense_date')
    search_fields=('title', 'notes')
    ordering=('-expense_date',)
    date_hierarchy = 'expense_date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display=(
        'user',
        'category',
        'month',
        'year',
        'amount_limit'
    )
    list_filter = ('year', 'month')