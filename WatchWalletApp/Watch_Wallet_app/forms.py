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


from django.forms.widgets import Select

class CategorySelect(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if hasattr(value, 'instance') and value.instance:
            category = value.instance
            option['attrs']['data-type'] = category.type
        return option

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'category',
            'amount',
            'date',
            'description'
        ]

        widgets = {
            'category': CategorySelect(attrs={'class': 'form-control'}),

            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '100'}
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
        transaction_type = kwargs.pop('transaction_type', None)

        super().__init__(*args, **kwargs)

        if user:
            if transaction_type:
                # Filter categories by user and type
                self.fields['category'].queryset = Category.objects.filter(
                    user=user, type=transaction_type
                )
            else:
                # If no type selected, show all user categories
                self.fields['category'].queryset = Category.objects.filter(
                    user=user
                )

            self.fields['category'].empty_label = 'Select a category'

        self.fields['transaction_type'].choices = [('', 'Select transaction type')] + list(self.fields['transaction_type'].choices)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError(
                "Amount must be greater than zero."
            )

        return amount

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('transaction_type')
        if category and transaction_type and category != '__add_new__' and hasattr(category, 'type') and category.type != transaction_type:
            raise forms.ValidationError("Selected category type does not match transaction type.")
        return cleaned_data


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'type']

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'type': forms.Select(
                attrs={'class': 'form-control'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].choices = [('', 'Select category type')] + list(self.fields['type'].choices)


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
                attrs={'class': 'form-control', 'step': '100'}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                type='expense'
            )
            self.fields['category'].empty_label = 'Select a category'

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
            'transaction_type',
            'category',
            'amount',
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
                attrs={'class': 'form-control', 'step': '100'}
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
        transaction_type = kwargs.pop('transaction_type', None)

        super().__init__(*args, **kwargs)

        if user:
            if transaction_type:
                self.fields['category'].queryset = Category.objects.filter(
                    user=user,
                    type=transaction_type
                )
            else:
                self.fields['category'].queryset = Category.objects.filter(
                    user=user
                )
            self.fields['category'].empty_label = 'Select a category'

        self.fields['transaction_type'].choices = [('', 'Select transaction type')] + list(self.fields['transaction_type'].choices)
        self.fields['frequency'].choices = [('', 'Select frequency')] + list(self.fields['frequency'].choices)

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
        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('transaction_type')

        if end_date and next_run_date:
            if end_date < next_run_date:
                raise forms.ValidationError(
                    "End date cannot be before next run date."
                )

        if category and transaction_type and hasattr(category, 'type') and category.type != transaction_type:
            raise forms.ValidationError(
                "Selected category type does not match transaction type."
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
                attrs={'class': 'form-control', 'step': '100'}
            ),

            'current_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '100'}
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