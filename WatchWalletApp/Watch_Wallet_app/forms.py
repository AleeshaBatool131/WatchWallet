from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Expense,Category

class ExpenseForm(forms.ModelChoiceField):
    class Meta: 
        model = Expense
        fields = ['title', 'amount', 'category', 'expense_date', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            }
#  def __init__(self, *args, **kwargs):
'''
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.none()

        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(user = user)
'''
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
