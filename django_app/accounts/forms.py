from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile


class RegisterForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='patient',
        widget=forms.Select(attrs={"class": "form-select"})
    )
    preferred_language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        initial='en',
        widget=forms.Select(attrs={"class": "form-select"})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"})
    )
    assigned_center = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Local Health Center / PHC (Optional)"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create password"
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password"
        })
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose Username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Username"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Password"
            }
        )
    )