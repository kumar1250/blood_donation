from django import forms
from .models import User  # ✅ custom user

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'blood_group', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username', 'autocomplete': 'new-username'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter password', 'autocomplete': 'new-password'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'autocomplete': 'off'}),
            'blood_group': forms.TextInput(attrs={'placeholder': 'Blood Group (e.g. A+)', 'autocomplete': 'off'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91XXXXXXXXXX', 'autocomplete': 'off'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter your address', 'rows': 3, 'autocomplete': 'off'}),
        }
