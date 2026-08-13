from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from .forms import RegisterForm, LoginForm


def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:

                messages.error(request, "Passwords do not match.")

            elif User.objects.filter(username=form.cleaned_data["username"]).exists():

                messages.error(request, "Username already exists.")

            elif User.objects.filter(email=form.cleaned_data["email"]).exists():

                messages.error(request, "Email already exists.")

            else:

                user = form.save(commit=False)
                user.set_password(password)
                user.save()

                messages.success(request, "Account created successfully!")

                return redirect("dashboard")

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


def user_login(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(request, "Welcome back!")

                return redirect("dashboard")

            else:

                messages.error(request, "Invalid username or password.")

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )
def user_logout(request):

    logout(request)

    messages.success(request, "You have been logged out successfully.")

    return redirect("login")