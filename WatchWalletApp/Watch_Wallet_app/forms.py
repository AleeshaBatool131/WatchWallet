from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Category,
    Transaction,
    Budget,
    RecurringTransaction,
    SavingsGoal
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: remove default Django help text
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""

        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label="Remember Me"
    )


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'category',
            'amount',
            'transaction_type',
            'date',
            'description'
        ]

        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),

            'amount': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'transaction_type': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'rows': 2,
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError(
                "Amount must be greater than zero."
            )

        return amount


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name']

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            )
        }


class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ['category', 'year', 'month', 'amount_limit']

        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'year': forms.NumberInput(
                attrs={
                    'min': 2000,
                    'max': 2100,
                    'class': 'form-control'
                }
            ),

            'month': forms.NumberInput(
                attrs={
                    'min': 1,
                    'max': 12,
                    'class': 'form-control'
                }
            ),

            'amount_limit': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            )

    def clean_amount_limit(self):
        amount = self.cleaned_data.get('amount_limit')

        if amount <= 0:
            raise forms.ValidationError(
                "Budget amount must be greater than zero."
            )

        return amount


class RecurringTransactionForm(forms.ModelForm):

    class Meta:
        model = RecurringTransaction

        fields = [
            'category',
            'amount',
            'transaction_type',
            'frequency',
            'next_run_date',
            'end_date',
            'description'
        ]

        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'amount': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'transaction_type': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'frequency': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'next_run_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'rows': 2,
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user
            )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError(
                "Amount must be greater than zero."
            )

        return amount

    def clean(self):
        cleaned_data = super().clean()

        next_run_date = cleaned_data.get('next_run_date')
        end_date = cleaned_data.get('end_date')

        if end_date and next_run_date:
            if end_date < next_run_date:
                raise forms.ValidationError(
                    "End date cannot be before next run date."
                )

        return cleaned_data


class SavingsGoalForm(forms.ModelForm):

    class Meta:
        model = SavingsGoal

        fields = [
            'name',
            'target_amount',
            'current_amount',
            'deadline'
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'target_amount': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'current_amount': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'deadline': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }

    def clean_target_amount(self):
        amount = self.cleaned_data.get('target_amount')

        if amount <= 0:
            raise forms.ValidationError(
                "Target amount must be greater than zero."
            )

        return amount

    def clean_current_amount(self):
        amount = self.cleaned_data.get('current_amount')

        if amount < 0:
            raise forms.ValidationError(
                "Current amount cannot be negative."
            )

        return amount